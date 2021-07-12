# IMPORTS
from flask import Flask, render_template            # The main thing - render_template is used to load HTML files
from markupsafe import Markup                       # Used to pass variables as HTML markup instead of plain text - https://tedboy.github.io/flask/generated/generated/flask.Markup.html

import pandas                                       # To read and manipulate the blockchain
import re                                           # Regular expressions to extract specific data

import users                                        # list of all currency things and their relevant properties
import blockchain_explorer                          # reads data from the blockchain without changing it
import graph_dealer                                 # creates nice graphs from the explorer's data

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
    line_chart = graph_dealer.plot_line_chart(blockchain.supply_over_time(), 'Supply Over Time', 'Date', '₡urrency Things')
    return render_template('flask_thing.html', TABLE=Markup(get_blockchain()), STATS=get_blockchain_stats())

# Domain variable! Use this to link to user's currency thing accounts, and then generate their data based on their ID
@app.route('/@<username>')
def user(username):
    USER = users.get_user(username)                                                 # gets the User object from the user.spy script
    table = get_user_trades(USER.mention)                                           # gets all of the user's trades
    print(USER)

    stats = get_user_things(USER.mention)                                           # getting the user's number statistics
    graph = get_user_graphs(USER.mention)
    
    # {{USERNAME}} tags in the .html became equal to the set variable; table value is passed as Markup to inject HTML code instead of plain text
    return render_template('user.html', USERNAME=username, TABLE=Markup(table), USER_ID=USER.id, STATS=stats, GRAPH=graph)    



######### BLOCKCHAIN FUNCTIONS / PANDAS

blockchain = blockchain_explorer.Blockchain()

### GENERAL FUNCTIONS

# Reads the block.chain file into a Pandas Dataframe
def get_blockchain():
    # Reading the blockchain
    blockchain = pandas.read_csv('block.chain')

    # Replacing user IDs with usernames
    blockchain.replace(users.replace_thing('mention', 'url'), inplace=True)

    # Displaying the emote image
    blockchain['PREV_HASH'] = blockchain['PREV_HASH'].apply(get_emote_url)

    # Formatting the date
    blockchain['TIME'] = pandas.to_datetime(blockchain['TIME']).dt.strftime('%d-%m-%Y')

    # Renaming the columns
    blockchain.columns = ['ID', 'INPUT', 'SIZE', 'OUTPUT', 'EMOTE', 'DATE']

    # Sorting by latest row
    blockchain.sort_index(axis=0, ascending=False, inplace=True)

    #  saves the dataframe as an HTML table with my custom class, no border, no row index, and without HTML code escaping
    return blockchain.to_html(classes='blockchain-table', index=False, border=0, escape=False)

def get_blockchain_stats():
    supply      = blockchain.get_supply()
    # mined       = blockchain.get_mined_filtered(8) # 8 is harcoded, maybe add a DATE column to the chain in future is necessary
    mined       = blockchain.get_things_mined_by_time()
    trades      = blockchain.get_trade_amount_by_time()
    user_trades = blockchain.get_trade_amount_by_time(user_only=True)
    user_num    = len(blockchain.user_list())
    biggest     = blockchain.get_biggest_trade(hours=24)

    stats = {'supply' : supply, 'mined' : mined, 'trades' : trades, 'user_trades' : user_trades, 'user_num' : user_num, 'biggest' : biggest}
    return stats

### USER SPECIFIC FUNCTIONS

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
    filter['TIME'] = pandas.to_datetime(blockchain['TIME']).dt.strftime('%d-%m-%Y')
    # Renaming the columns
    filter.columns = ['ID', 'INPUT', 'SIZE', 'OUTPUT', 'EMOTE', 'DATE']

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

    return networth_graph



######### GETTING EMOTES
EMOTE_URL = 'https://cdn.discordapp.com/emojis/{}.png'
IMG_TAG     = '<img src={} height="32px">'

# Gets the direct URL to an emote image using the discord <:emote:123> code
def get_emote_url(emote_code: str):
    # Does no formating if the code doesn't start with <
    if not(emote_code.startswith('<')):
        return emote_code

    # extracts the number ID - /d+ matches all digits
    id = re.findall(r'\d+', emote_code)[0]

    emote_url = EMOTE_URL.format(id)
    img_tag = IMG_TAG.format(emote_url)
    
    return img_tag



# Runs the server
if __name__ == '__main__':
    app.run(debug=True)