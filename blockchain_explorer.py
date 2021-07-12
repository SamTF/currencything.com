### This script only explores the blockchain. It does not create or verify blocks.

### IMPORTS
import pandas as pd
from datetime import datetime, timedelta

# Constants
BLOCKCHAIN = 'block.chain'              # the name of the local blockchain file stored on disk
CREATOR_ID = 840976021687762955         # The User that sends rewards to miners


### THE BLOCKCHAIN CLASS
class Blockchain:

    # Initialising the class
    def __init__(self):
        self.chain = pd.read_csv(BLOCKCHAIN)
        self.chain['SIZE'] = pd.to_numeric(self.chain['SIZE'])                          # Converts the SIZE column into INT type; otherwise it assumes STRING type
        self.chain['TIME'] = pd.to_datetime(self.chain['TIME'])                         # Converts the TIME column into datetime format
    
    
    ### GENERAL STATS ######

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
    
    
    def get_trades_by_time(self, hours:int = 24) -> pd.DataFrame:
        '''
        Returns the trades that occured in the last X hours.

        hours: amount of hours to subtract from current time. (default = 24)
        '''
        date = datetime.now() - timedelta(hours=hours)                                  # Gets the datetime value a specified amount of hours ago
        filter = self.chain.loc[self.chain['TIME'] > date]                              # Gets all blockchain trades with a time greater than that value

        return filter
    

    def get_things_mined_by_time(self, hours:int = 24) -> int:
        '''
        Returns the amount of currency things mined in the last h hours.

        hours: amount of hours to subtract from current time. (default = 24)
        '''
        rows = self.get_trades_by_time(hours)                                           # Gets all the trades that occured in the last specified hours
        mined = rows.loc[rows['INPUT'] == f'<@{CREATOR_ID}>']                           # Gets all trades where the Currency Thing Bot is the one sending things
        mined = mined['SIZE'].sum()                                                     # Sums the size of currency things sent

        return mined

    
    def get_trade_amount_by_time(self, hours:int = 24, user_only:bool = False) -> int:
        '''
        Returns the amount of trades that occured in the past h hours

        hours: amount of hours to subtract from current time. (default = 24)
        user_only: only displays trades executed by users and not by the Currency Thing bot
        '''
        rows = self.get_trades_by_time(hours)                                           # Gets all the trades that occured in the last specified hours

        if user_only:
            rows = rows.loc[rows['INPUT'] != f'<@{CREATOR_ID}>']                        # Only count rows where the Currency Thing Bot was not involved

        return len(rows.index)
    

    def get_biggest_trade(self, hours:int = 0) -> int:
        '''
        Returns the trade with the largest size.

        hours: if set, only counts trades in the last h hours. Otherwise, counts the entire blockchain
        '''
        rows = self.get_trades_by_time(hours) if hours else self.chain                  # checks entire blockchain if no time limit specified
        rows.sort_values('SIZE', ascending=False, inplace=True)                         # Sorts rows by trade size in descending order

        return rows.iloc[0]['SIZE']
    

    def get_trade_amount_by_day(self) -> pd.DataFrame:
        '''
        Returns the quantity of transactions per day on the blockchain.
        '''
        trades = self.chain.copy()
        trades['TIME'] = trades['TIME'].dt.date
        trades = trades.groupby('TIME').count()
        trades.drop(['ID', 'INPUT', 'OUTPUT', 'PREV_HASH'], axis=1, inplace=True)

        return trades
    

    def supply_over_time(self) -> pd.DataFrame:
        '''
        Returns the total amount of currency things in circulation per day.
        '''
        INPUT = self.chain.loc[self.chain['INPUT'] == f'<@{CREATOR_ID}>']               # All currency things sent by this user
        INPUT['TIME'] = INPUT['TIME'].dt.date                                           # Converts the datetime to date
        INPUT.drop(['ID', 'INPUT', 'OUTPUT', 'PREV_HASH'], axis=1, inplace=True)        # Drops unnecessary columns
        supply = INPUT.groupby('TIME').sum()                                            # Sums all currency things mined per day
        supply = supply.cumsum(axis=0)                                                  # Gets the cumulative sum by date

        return supply
    

    def supply_over_tx(self):
        '''
        Returns the total amount of currency things in circulation at each transaction ID
        '''
        INPUT = self.chain.loc[self.chain['INPUT'] == f'<@{CREATOR_ID}>']               # All currency things sent by this user
        INPUT.drop(['ID', 'INPUT', 'OUTPUT', 'PREV_HASH', 'TIME'], axis=1, inplace=True)# Removes unnecessary columns

        return INPUT.cumsum()                                                           # cum

    
 

    


    ### USER SPECIFIC STATS ######

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


        


        

# Runs the server
if __name__ == '__main__':
    blockchain = Blockchain()
else:
    print("BLOCKCHAIN EXPLORER IMPORTED")