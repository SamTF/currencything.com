# IMPORTS
from flask import Flask, render_template, jsonify, request            # The main thing - render_template is used to load HTML files
from markupsafe import Markup
from matplotlib import set_loglevel                       # Used to pass variables as HTML markup instead of plain text - https://tedboy.github.io/flask/generated/generated/flask.Markup.html

import pandas                                       # To read and manipulate the blockchain
import re                                           # Regular expressions to extract specific data

import users                                        # list of all currency things and their relevant properties
import blockchain_explorer                          # reads data from the blockchain without changing it
import graph_dealer                                 # creates nice graphs from the explorer's data
from period import Period, str_to_enum              # Time Period Enum


# https://pypi.org/project/pyChart.JS/

#### Flask directory:
# /app
#     - app_runner.py
#     /services
#         - app.py 
#     /templates
#         - mainpage.html
#     /static
#         /css
#             - mainpage.css
#         /images
#             - worms.png
###########################


######### WEBSITE FUNCTIONS / PAGES

# Initialises Flask
app = Flask(__name__)

# The default domain directory (index.html)
@app.route('/')
def home():
    graph_dealer.plot_line_chart(blockchain.supply_over_time(),             'supply',       'Supply Over Time',         'Date',         '₡urrency Things',  True)
    graph_dealer.plot_line_chart(blockchain.mined_per_day(),                'mined',        'Things Mined Per Day',     'Date',         '₡urrency Things',  True)
    graph_dealer.plot_line_chart(blockchain.get_trade_data_by_day(),        'trades',       'Trades Over Time',         'Date',         '# Of Trades',      True)
    graph_dealer.plot_line_chart(blockchain.get_trade_data_by_day(True),    'user_trades',  'User Trades Over Time',    'Date',         '# Of Trades',      True)
    graph_dealer.plot_bar_chart(blockchain.biggest_trade_over_time(),       'big_trades',   'Biggest Trade Over Time',  'Trade ID',     'Trade Size',       False)

    # blockchain.who_giveth_more()
    # blockchain.who_mined_more()

    # Reads the blockchain file from disk again to catch any changes. Hopefully this won't somehow overload the VM disk with read operations.
    blockchain.reload_blockchain()

    return render_template('flask_thing.html', TABLE=Markup(get_blockchain()), STATS=get_blockchain_stats(), LABELS=list(get_balance_all().keys()), VALUES=list(get_balance_all().values()))

# Domain variable! Use this to link to user's currency thing accounts, and then generate their data based on their ID
@app.route('/@<username>')
def user(username):
    USER = users.get_user(username)                                                 # gets the User object from the user.spy script

    # if someone types a random username, send them to the homepage instead of getting an error page
    if not USER:
        print(f'[flask_website.py] >>> User [{username}] does not exist')
        print('[flask_website.py] >>> Returning to homepage')
        return render_template('flask_thing.html', TABLE=Markup(get_blockchain()), STATS=get_blockchain_stats())

    table = get_user_trades(USER.mention)                                           # gets all of the user's trades
    stats = get_user_things(USER.mention)                                           # getting the user's number statistics
    get_user_graphs(USER.mention)                                                   # getting the user's graphs
    
    # {{USERNAME}} tags in the .html became equal to the set variable; table value is passed as Markup to inject HTML code instead of plain text
    return render_template('user.html', USERNAME=username, TABLE=Markup(table), USER_ID=USER.id, STATS=stats)    



### BUTTON FUNCTIONS THAT RETURN JSON
# Not actual pages
# from https://www.py4u.net/discuss/278063 & https://stackoverflow.com/questions/36620864/passing-variables-from-flask-back-to-ajax

@app.route('/background_process_test/<data>')
def background_process_test(data):
    print ("\n\n\n [ B A C K G R O U N D  P R O C E S S  T E S T ]")
    print(data)
    print("\n\n\n")

    return jsonify(a = 1, b =2 , c =3)

@app.route('/get_json')
def get_json():
    print('\nget_json\n\n')

    d = {'a' : 9, 'b' : 8, 'c' : 7}
    return d
    # return jsonify(a = 1, b =2 , c =3)


# Function called from HTML Buttons on the main page to update the stats information to a different time period
# Receives var 'period' from the page, returns a JSON object
@app.route('/update_stats', methods=['GET'])
def update_stats():
    period = request.args.get('period')                                                         # gets the var sent by the JSON request in JS
    
    period_enum = str_to_enum(period)                                                           # converts the string var into a Period Enum
    
    stats = get_blockchain_stats(period_enum)                                                   # gets blockchain stats for the relevant time period using the enum
    stats = dict([key, int(value)] for key, value in stats.items())                             # converts the numpy values into integers
    
    stats['period'] = period                                                                    # adds the specified time period to the dictionary
    stats['text'] = period_enum.value[1]                                                        # adds the Enum's text value to the dictionary

    return stats

# Function called from JQuery to get the Achievement trades - in future, save this to a file and read that instead of running the functions every time?
@app.route('/get_achievements')
def get_achievements():
    ### OLD METHOD
    # i = str(blockchain.get_supply())[:-3]                                                       # removes the last 3 characters
    # thousands = int(i) * 1000                                                                   # multiplies the thousandth figures by 1000
    
    # milestones = range(1000, thousands + 1000, 1000)
    
    # # A list of tuples containing the Milestone reached, and the Trade ID where it was reached, for each milestone specified above
    # tup = tuple([(x, blockchain.who_mined_xth_thing(x)) for x in milestones])

    ### NEW METHOD
    tup = blockchain.get_mining_milestones()

    return jsonify(tup)


######### BLOCKCHAIN FUNCTIONS / PANDAS

blockchain = blockchain_explorer.Blockchain()

### GENERAL FUNCTIONS ######

# Reads the block.chain file into a Pandas Dataframe
def get_blockchain():
    # Reading the blockchain
    blockchain = pandas.read_csv('block.chain')

    # Replacing user IDs with usernames
    blockchain.replace(users.replace_thing('mention', 'url'), inplace=True)

    # Displaying the emote image
    blockchain['PREV_HASH'] = blockchain['PREV_HASH'].apply(get_emote_url)

    # Formatting the date
    blockchain['TIME'] = pandas.to_datetime(blockchain['TIME']).dt.strftime('%d/%m') #'%d-%m-%Y'

    # Renaming the columns
    blockchain.columns = ['ID', 'INPUT', 'SIZE', 'OUTPUT', 'EMOTE', 'DATE']

    # Sorting by latest row
    blockchain.sort_index(axis=0, ascending=False, inplace=True)

    #  saves the dataframe as an HTML table with my custom class, no border, no row index, and without HTML code escaping
    return blockchain.to_html(classes='blockchain-table', index=False, border=0, escape=False)


# Gets general statistics for the blockchain as a whole
def get_blockchain_stats(period: Period = Period.DAILY):
    supply      = blockchain.get_supply()
    # mined       = blockchain.get_mined_filtered(8) # 8 is harcoded, maybe add a DATE column to the chain in future is necessary
    mined       = blockchain.get_things_mined_by_time(days=period.value[0])
    trades      = blockchain.get_trade_amount_by_time(days=period.value[0])
    user_trades = blockchain.get_trade_amount_by_time(days=period.value[0], user_only=True)
    user_num    = len(blockchain.user_list())
    biggest     = blockchain.get_biggest_trade(days=period.value[0])

    stats = {'supply' : supply, 'mined' : mined, 'trades' : trades, 'user_trades' : user_trades, 'user_num' : user_num, 'biggest' : biggest}
    return stats


# Gets the balance of all users
def get_balance_all():
    balances = blockchain.get_balance_all()
    user_lookup = users.replace_thing('mention', 'name')
    
    return {user_lookup[user]: b for user, b in balances.items()}



### USER SPECIFIC FUNCTIONS ######

# Gets all trades a user was involved in using their discord @mention
def get_user_trades(mention: str):
    blockchain = pandas.read_csv('block.chain')

    # Filtering all rows where User is either Input or Output
    filter = blockchain.loc[(blockchain['INPUT'] == mention) | (blockchain['OUTPUT'] == mention)]

    # Replacing user IDs with usernames
    filter.replace(users.replace_thing('mention', 'url'), inplace=True)

    # Displaying the emote image
    # filter.replace('^<:[a-zA-Z]+:[0-9]+>$', 'emote.png', regex=True, inplace=True) : from https://regex-generator.olafneumann.org
    filter['PREV_HASH'] = filter['PREV_HASH'].apply(get_emote_url)

    # Formatting the date
    filter['TIME'] = pandas.to_datetime(blockchain['TIME']).dt.strftime('%d/%m')
    
    # Renaming the columns
    filter.columns = ['ID', 'INPUT', 'SIZE', 'OUTPUT', 'EMOTE', 'DATE']

    # Sorting by latest row
    filter.sort_index(axis=0, ascending=False, inplace=True)

    return filter.to_html(classes='blockchain-table', index=False, border=0, escape=False)


# Gets all number statistics relative to the chosen user
def get_user_things(user: str) -> dict:
    balance     = blockchain.get_balance            (user)
    mined       = blockchain.get_things_mined       (user)
    sent        = blockchain.get_things_sent        (user)
    received    = blockchain.get_things_received    (user)
    trades      = blockchain.get_trade_participation(user)
    big_sent    = blockchain.get_biggest_sent       (user)
    big_received= blockchain.get_biggest_received   (user)

    stats = {'balance' : balance, 'mined' : mined, 'sent' : sent, 'received' : received, 'trades' : trades, 'big_sent' : big_sent, 'big_received' : big_received}

    return stats


# Gets all the graphs statistics of the chosen user
def get_user_graphs(user: str):
    networth_data = blockchain.networth_over_time(user)
    networth_graph = graph_dealer.plot_networth(networth_data)

    trades = blockchain.get_trade_data_by_day(True, user)
    trades_graph = graph_dealer.plot_line_chart(trades, 'tx', 'Trades Per Day', 'Day', '# Of Trades', date_index=True)



### GETTING EMOTES ######
EMOTE_URL = 'https://cdn.discordapp.com/emojis/{}.png'
IMG_TAG     = '<img src={} height="32px">'

# Gets the direct URL to an emote image using the discord <:emote:123> code
def get_emote_url(emote_code: str):
    # Does no formating if the code doesn't start with <
    if not(emote_code.startswith('<')):
        return emote_code

    # extracts the number ID - /d+ matches all digits
    id = re.findall(r'\d+', emote_code)[0]

    # gets the direct link to the image on discord's cdn
    emote_url = EMOTE_URL.format(id)

    # formats that link as an HTML IMG tag
    img_tag = IMG_TAG.format(emote_url)
    
    return img_tag



# Runs the server
if __name__ == '__main__':
    app.run(debug=True)