### This script only explores the blockchain. It does not create or verify blocks.

### IMPORTS
import pandas as pd
from datetime import datetime, timedelta

# Suppressing the annoying SettingWithCopy warning
pd.options.mode.chained_assignment = None

# Constants
BLOCKCHAIN = 'block.chain'              # the name of the local blockchain file stored on disk
CREATOR_ID = 840976021687762955         # The User that sends rewards to miners


###### THE BLOCKCHAIN CLASS ##############################################################################################################
class Blockchain:

    # Initialising the class
    def __init__(self):
        self.chain = pd.read_csv(BLOCKCHAIN)
        self.chain['SIZE'] = pd.to_numeric(self.chain['SIZE'])                          # Converts the SIZE column into INT type; otherwise it assumes STRING type
        self.chain['TIME'] = pd.to_datetime(self.chain['TIME'])                         # Converts the TIME column into datetime format
    
    
    # Loading the blockchain file from disk again, to get latest changes
    def reload_blockchain(self):
        self.chain = pd.read_csv(BLOCKCHAIN)
        self.chain['SIZE'] = pd.to_numeric(self.chain['SIZE'])                          # Converts the SIZE column into INT type; otherwise it assumes STRING type
        self.chain['TIME'] = pd.to_datetime(self.chain['TIME'])                         # Converts the TIME column into datetime format
    
    

    ###### GENERAL STATS #################################################################################################################

    # Gets the total amount of currency things in circulation / the amount mined
    def get_supply(self) -> int:
        INPUT = self.chain.groupby(['INPUT']).sum()                                     # INPUT  Dataframe - sums all currency things SENT BY each user - where the user is on the INPUT  side of the trade
        supply = INPUT.loc[f'<@{CREATOR_ID}>']['SIZE']                                  # Sums all currency things sent by the discord bot - aka total supply
        print(f'[BLOCKCHAIN] >>> Current supply: {supply}')

        return supply
    

    def user_list(self) -> list:
        '''
        Returns a list of all users to ever received a currency thing.
        '''
        return self.chain.groupby(['OUTPUT']).sum().index.to_list()                     # getting a list of all the users that own currency things as discord @mentions

    def get_mined_filtered(self, filter: int, last: bool = True) -> int:
        '''
        Filtering only how many currency things were mined in the last/first x trades.
        Returns the sum of things sent in those trades.

        filter: how many trades to get;
        last: if True, filters from the end of the blockchain. if False, filters from the start
        '''
        mined = self.chain.loc[self.chain['INPUT'] == f'<@{CREATOR_ID}>']               # Gets all trades where the Currency Thing Bot is the one sending things
        filtered = mined.tail(filter) if last else mined.head(filter)                   # Filters  only the last or first X trades
        mined_filtered = filtered['SIZE'].sum()                                         # Sums the size of currency things sent

        return mined_filtered
    
    
    def get_trades_by_time(self, days:int = 1) -> pd.DataFrame:
        '''
        Returns the trades that occured in the last X days.

        days: amount of days to subtract from current datetime. (default = 1)
        '''
        date = datetime.now() - timedelta(days=days)                                    # Gets the datetime value a specified amount of hours ago
        filter = self.chain.loc[self.chain['TIME'] > date]                              # Gets all blockchain trades with a time greater than that value

        return filter
    

    def get_things_mined_by_time(self, days:int = 1) -> int:
        '''
        Returns the total amount of currency things mined in the last X days as an INT.

        days: amount of days to subtract from current datetime. (default = 1)
        '''
        rows = self.get_trades_by_time(days) if days else self.chain                    # checks entire blockchain, or last few days if "days" value is specified
        mined = rows.loc[rows['INPUT'] == f'<@{CREATOR_ID}>']                           # Gets all trades where the Currency Thing Bot is the one sending things
        mined = mined['SIZE'].sum()                                                     # Sums the size of currency things sent

        return mined

    
    def get_trade_amount_by_time(self, days:int = 1, user_only:bool = False, specified_user: str = None) -> int:
        '''
        Returns the TOTAL amount of trades that occured in the past days as an INT.

        days: amount of days to subtract from current datetime. (default = 1)
        user_only: only displays trades executed by users and not by the Currency Thing bot
        specified_user: only displays trades involving this specified user
        '''
        rows = self.get_trades_by_time(days) if days else self.chain                    # checks entire blockchain, or last few days if "days" value is specified

        if user_only:
            rows = rows.loc[rows['INPUT'] != f'<@{CREATOR_ID}>']                        # Only count rows where the Currency Thing Bot was not involved
        
        if specified_user:
            rows = rows.loc[(rows['INPUT'] == specified_user) | (rows['OUTPUT'] == specified_user)]    # Only count rows where the specified user was involved

        return len(rows.index)
    

    def get_biggest_trade(self, days:int = 0) -> int:
        '''
        Returns the trade with the largest size.

        days: if set, only counts trades in the last X days. Otherwise, counts the entire blockchain.
        '''
        rows = self.get_trades_by_time(days) if days else self.chain                    # checks entire blockchain if no time limit specified
        rows.sort_values('SIZE', ascending=False, inplace=True)                         # Sorts rows by trade size in descending order

        if rows.empty: return 0                                                         # 0 in case there have been no trades in the specified timeframe

        return rows.iloc[0]['SIZE']
    

    def get_trade_data_by_day(self, user_only:bool = False, specific_user: str = None) -> pd.DataFrame:
        '''
        Returns the quantity of transactions PER DAY on the blockchain as a DataFrame.

        user_only: only displays trades executed by users and not by the Currency Thing bot
        '''
        trades = self.chain.copy()

        if user_only:
            trades = trades.loc[trades['INPUT'] != f'<@{CREATOR_ID}>']                  # Only count rows where the Currency Thing Bot was not involved
        
        if specific_user:
            trades = trades.loc[(trades['INPUT'] == specific_user) | (trades['OUTPUT'] == specific_user)]    # Only count rows where the specified user was involved

        trades['TIME'] = trades['TIME'].dt.date
        trades = trades.groupby('TIME').count()
        trades.drop(['ID', 'INPUT', 'OUTPUT', 'PREV_HASH'], axis=1, inplace=True)

        return trades
    

    def supply_over_time(self) -> pd.DataFrame:
        '''
        Returns the total amount of currency things in circulation per day.
        '''
        INPUT = self.chain.loc[self.chain['INPUT'] == f'<@{CREATOR_ID}>']               # All currency things sent by the Currency Thing bot (mined)
        INPUT['TIME'] = INPUT['TIME'].dt.date                                           # Converts the datetime to date
        INPUT.drop(['ID', 'INPUT', 'OUTPUT', 'PREV_HASH'], axis=1, inplace=True)        # Drops unnecessary columns
        supply = INPUT.groupby('TIME').sum()                                            # Sums all currency things mined per day
        supply = supply.cumsum(axis=0)                                                  # Gets the cumulative sum by date

        return supply
    

    def supply_over_tx(self):
        '''
        Returns the total amount of currency things in circulation at each transaction ID
        '''
        INPUT = self.chain.loc[self.chain['INPUT'] == f'<@{CREATOR_ID}>']               # All currency things sent by the Currency Thing bot (mined)
        INPUT.drop(['ID', 'INPUT', 'OUTPUT', 'PREV_HASH', 'TIME'], axis=1, inplace=True)# Removes unnecessary columns

        return INPUT.cumsum()                                                           # cum
    

    def mined_per_day(self):
        trades = self.chain.copy()
        mined = trades.loc[trades['INPUT'] == f'<@{CREATOR_ID}>']                       # Gets all trades where the Currency Thing Bot is the one sending things
        mined['TIME'] = mined['TIME'].dt.date                                           # Converts the datetime to date
        mined = mined.groupby('TIME').sum()                                             # Groups by date and sums all size values at each day

        return mined
    

    def biggest_trade_over_time(self):
        '''
        Finds the biggest trade size at every moment in the blockchain.
        Returns a pandas dataframe.
        '''
        big_trades = []
        biggest_trade = 0

        for index, row in self.chain.iterrows():
            size = row['SIZE']
            
            # short and simple version
            if size > biggest_trade:
                data = (row['ID'], size)
                biggest_trade = size
                big_trades.append(data)
            
            # Extended version - needed for chartJS
            # else:
            #     data = (row['ID'], biggest_trade)
            
            # big_trades.append(data)
        
        big_trades_df = pd.DataFrame(big_trades, columns=['ID', 'SIZE'])
        big_trades_df.set_index('ID', inplace=True)

        print('BIGGEST TRADE OVER TIME')
        print(big_trades_df)
        return big_trades_df


    
 

    


    ###### USER SPECIFIC STATS ##############################################################################################################

    # Gets the amount of currency things held by a user
    def get_balance(self, user: str) -> int:
        '''
        Gets the amount of currency things held by a user.

        user : discord @mention : <@123456789>
        '''

        OUTPUT = self.chain.groupby(['OUTPUT']).sum()                                   # OUTPUT Dataframe - sums all currency things SENT TO each user - where the user is on the OUTPUT side of the trade
        INPUT = self.chain.groupby(['INPUT']).sum()                                     # INPUT  Dataframe - sums all currency things SENT BY each user - where the user is on the INPUT  side of the trade

        try:    sent = INPUT.loc[user]['SIZE']                                          # Check in case a user has only received and never sent to avoid Key Errors in the INPUT table
        except: sent = 0       

        return OUTPUT.loc[user]['SIZE'] - sent                                          # Subtracts the amount sent (INPUT table) from the amount received (OUTPUT table) to get the current balance
    

    # Getting the balance of ALL users
    def get_balance_all(self) -> dict:
        '''
        Gets the amount of currency things held by any address that has ever received currency things.

        Returns a dictionary { @mention : balance}
        '''

        balances = {}                                                                   # dictionary to store user @mentions and their current balance
        users = self.chain.groupby(['OUTPUT']).sum().index.to_list()                    # getting a list of all the users that own currency things as discord @mentions

        for user in users:
            b = self.get_balance(user)
            balances[user] = b
        
        return balances

    

    def get_things_mined(self, user: str) -> int:
        '''
        Gets the total amount of currency things that a user has mined.

        user : discord @mention : <@123456789>
        '''
        # Filters rows where the INPUT was Currency Thing AND the OUTPUT was the desired user
        filter = self.chain.loc[(self.chain['INPUT'] == f'<@{CREATOR_ID}>') & (self.chain['OUTPUT'] == user)]

        # Sums the results
        things_mined = filter['SIZE'].sum()
        
        return things_mined


    def get_things_sent(self, user: str) -> int:
        '''
        Gets the total amount of currency things that a user has sent to others.

        user : discord @mention : <@123456789>
        '''
        INPUT = self.chain.groupby(['INPUT']).sum()                                     # INPUT  Dataframe - sums all currency things SENT BY each user - where the user is on the INPUT side of the trade

        try:    sent = INPUT.loc[user]['SIZE']                                          # Check in case a user has only received and never sent to avoid Key Errors in the INPUT table
        except: sent = 0

        return sent
    

    def get_things_received(self, user: str) -> int:
        '''
        Gets the amount of currency things sent to this user by others.

        user : discord @mention : <@123456789>
        '''
        # Filters rows where the INPUT was NOT Currency Thing AND the OUTPUT was the desired user
        filter = self.chain.loc[(self.chain['INPUT'] != f'<@{CREATOR_ID}>') & (self.chain['OUTPUT'] == user)]

        # Sums the results
        things_received = filter['SIZE'].sum()
        
        return things_received
    

    def get_trade_participation(self, user: str) -> int:
        '''
        Gets the amount of trades a user participated in.

        user : discord @mention : <@123456789>
        '''

        # Gets all rows that contain the user in either input or output
        filter = self.chain.loc[(self.chain['INPUT'] == user) | (self.chain['OUTPUT'] == user)]

        # Gets the amount of rows in the filtered dataframe
        participation = len(filter.index)

        return participation
    

    def get_biggest_sent(self, user: str) -> int:
        '''
        The biggest amount of currency things that this user has sent someone.

        user : discord @mention : <@123456789>
        '''

        # Gets all trades where the user was on the INPUT.
        filter = self.chain.loc[self.chain['INPUT'] == user]

        # Returns 0 if user was never the input.
        if filter.empty: return 0

        # Sorts rows by trade size in descending order
        filter.sort_values('SIZE', ascending=False, inplace=True)

        # Gets the SIZE value of the first row
        big_sent = filter.iloc[0]['SIZE']

        return big_sent
    

    def get_biggest_received(self, user: str) -> int:
        '''
        The biggest amount of currency things sent to this user.

        user : discord @mention : <@123456789>
        '''

        # Filters rows where Currency Thing was NOT the INPUT, and the user was the OUTPUT.
        filter = self.chain.loc[(self.chain['INPUT'] != f'<@{CREATOR_ID}>') & (self.chain['OUTPUT'] == user)]

        # Returns 0 if user was never the output.
        if filter.empty: return 0

        # Sorts rows by trade size in descending order
        filter.sort_values('SIZE', ascending=False, inplace=True)

        # Gets the SIZE value of the first row
        big_received = filter.iloc[0]['SIZE']

        return big_received



    ### USER GRAPHS

    def networth_over_time(self, user: str) -> pd.DataFrame:
        '''
            The cumulative amount of currency things held by the user over time.
            Sums things received and subtracts things sent by trade ID.

            user : discord @mention : <@123456789>
        '''

        OUTPUT  = self.chain.loc[self.chain['OUTPUT']   == user]                    # All currency things received by this user
        INPUT   = self.chain.loc[self.chain['INPUT']    == user]                    # All currency things sent by this user

        INPUT['SIZE'] = INPUT['SIZE'] * - 1                                         # Turns sent things into negtaive transactions

        networth = pd.concat([OUTPUT, INPUT])                                       # Combines both dataframes
        networth.set_index('ID', drop=True, inplace=True)                           # Sets the ID column as Index just to keep it clean
        networth = networth.sort_index(axis=0)                                      # Sorts the values chronologically by ID
        networth.drop(['INPUT', 'OUTPUT', 'PREV_HASH'], axis=1, inplace=True)       # Removes unnecessary columns

        networth = networth.cumsum()                                                # Finally, the cumulative amount of currency things held at each point

        return networth
    

    
    ###### USER ACHIEVEMENTS ##############################################################################################################
    def who_mined_xth_thing(self, thing):
        '''
        Finds the user who mined the Nth currency thing. Returns the trade ID.

        thing: the Nth thing.
        '''
        import users

        df = self.chain.loc[self.chain['INPUT'] == f'<@{CREATOR_ID}>']              # All currency things sent by the Currency Thing bot (mined)
        df['SUPPLY'] = self.supply_over_tx()['SIZE']                                # Adds the total supply at each point as a column to the dataframe

        filter = df.loc[df['SUPPLY'] <= thing]                                      # Getting all trades where the supply is less than the amount we're looking for (anything after that is after the nth thing was mined, so the last trade before then was the miner)
        winner = filter.tail(1)[['OUTPUT', 'TIME']]                                 # Gets the last row before the limit - the winner - only the Output and Time columns

        winner.replace(users.replace_thing('mention', 'name'), inplace=True)        # Replacing user discord mention with username

        # Getting the direct values
        user = winner.iloc[0]['OUTPUT']
        date = winner.iloc[0]['TIME'].date()
        trade_id = winner.index.tolist()[0]
        msg = f'Currency Thing #{thing} was mined by {user} on {date} / trade #{trade_id}'

        print(msg)

        # All we need for the website is the Trade ID. The other data could be used for the discord bot. Also maybe save this info to a file instead of checking every time?
        return trade_id
    

    def who_giveth_more(self):
        '''
        Finds the user that has given away the most currency things to other users.
        '''

        sent = self.chain.groupby(['INPUT']).sum()                                      # INPUT Dataframe - sums all currency things SENT BY each user - where the user is on the INPUT  side of the trade
        sent.drop(f'<@{CREATOR_ID}>', inplace=True)                                     # Dropping the Currency Thing Bot from the list
        sent.drop('ID', axis=1, inplace=True)                                           # Dropping the trade ID sum: not needed
        sent = sent.sort_values(by='SIZE', ascending=False)                             # Sorting values by biggest sum traded

        big_giver = sent.head(1)                                                        # Getting the first value: the biggest giver

        print('\n\n\n')
        print(big_giver)


    def who_mined_more(self):
        '''
        Finds the user who has mined the most currency things.
        '''

        filter = self.chain.loc[(self.chain['INPUT'] == f'<@{CREATOR_ID}>')]            # Filters rows where the INPUT was Currency Thing
        miners_df = filter.groupby('OUTPUT').sum()                                      # Groups by OUTPUT user and sums the total
        miners_df = miners_df.sort_values(by='SIZE', ascending=False).drop('ID', axis=1)# Sorts by ascending SIZE and drops the ID column
    

    # maybe also have weekly/monthly versions of these achievements?

        

        



        


        

# Runs the server
if __name__ == '__main__':
    blockchain = Blockchain()
else:
    print("BLOCKCHAIN EXPLORER IMPORTED")