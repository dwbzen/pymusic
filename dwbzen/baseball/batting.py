'''
Created on Apr 22, 2023

@author: dwbze
'''

import pandas as pd
import argparse
import json
from baseball.databank import BaseballDatabank

class Batting(BaseballDatabank):
    """
    """

    batting_db_dict = {
'playerID': 'Player ID code',
'yearID': 'Year',
'stint': 'order of appearances within a season',
'teamID':'Team',
'lgID':'League',
'G':'Games',
'AB':'At Bats',
'R':'Runs',
'H':'Hits',
'2B':'Doubles',
'3B':'Triples',
'HR':'Homeruns',
'RBI':'Runs Batted In',
'SB':'Stolen Bases',
'CS':'Caught Stealing',
'BB':'Base on Balls',
'SO':'Strikeouts',
'IBB':'Intentional walks',
'HBP':'Hit by pitch',
'SH':'Sacrifice hits',
'SF':'Sacrifice flies',
'GIDP':'Grounded into double plays' }

    def __init__(self,  start_year=1905, end_year=2022):
        """
        """
        super().__init__(start_year, end_year)
        # 20 star players 
        # aaronha01 - Hank Aaron
        # bondsba01 - Barry Bonds
        # cobbty01  - Ty Cobb
        # dimagjo01 - Joe DiMaggio
        # gehrilo01 - Lou Gehrig
        # hornsro01 - Rogers Hornsby
        # jacksjo01 - "Shoeless" Joe Jackson
        # jacksre01 - Reggie Jackson
        # jeterde01 - Derek Jeter
        # judgeaa01 - Aaron Judge
        # mantlmi01 - Mickey Mantle
        # marisro01 - Roger Eugene Maris
        # mayswi01  - Willie Mays
        # robinfr02 - Frank Robinson
        # robinja02 - Jackie Robinson
        # rodrial01 - Alex Rodriguez
        # ruthba01  - Babe Ruth
        # troutmi01 - Mike Trout
        # willite01 - Ted Williams
        # yastrca01 - Carl Yastrzemski
        # ohtansh01 - Shohei Ohtani

        self._star_player_list = ["aaronha01", "bondsba01", "cobbty01", "dimagjo01", "gehrilo01",\
            "hornsro01", "jacksjo01", "jacksre01", "jeterde01","judgeaa01", \
            "mantlmi01","marisro01", "mayswi01",  "robinfr02","robinja02",\
            "rodrial01","ruthba01", "troutmi01", "willite01", "yastrca01" ]
        self._splist = ['mantlmi01','aaronha01','robinja02','mayswi01','dimagjo01','judgeaa01','rodrial01']
        self._load_player_batting()
    
    def _load_player_batting(self):
        #
        # group by player and sum the columns
        # need to recalculate the batting stats columns
        #
        self._player_batting_df = self._batting_df.groupby('playerID').sum(numeric_only=True)
        player_batting_averages = self._player_batting_df[['AB','H']].apply(lambda df: round(df['H']/df['AB'],3), axis=1)
        self._player_batting_df['AVG'] = player_batting_averages
        
        # recalculate SLG, OBP
        # slugging pct
        SLG = self._player_batting_df[['total_bases', 'AB']].apply(lambda df: round(df['total_bases']/df['AB'],3),axis=1 )
        self._player_batting_df['SLG'] = SLG
        
        # on-base percentage
        on_base_percentage = self._player_batting_df[['AB', 'H', 'HBP', 'BB', 'SF']].\
            apply(lambda df: round(((df['H'] + df['BB'] + df['HBP']) /(df['AB'] +  df['BB'] + df['HBP']+ df['SF'])),3), axis=1) 
        self._player_batting_df['OBP'] = on_base_percentage
        
        # add years played column - NOTE the index must be playerID for this to work
        years_played = self._batting_df.groupby('playerID').size()   #number of years
        self._player_batting_df['years'] = years_played
        
        # add first and last year in the majors
        self._player_batting_df['first_year'] = self._batting_df.groupby('playerID').min()['yearID'] 
        self._player_batting_df['last_year'] = self._batting_df.groupby('playerID').max()['yearID']
        # 
        # reset the index
        self._player_batting_df = self._player_batting_df.reset_index()
        
        # add the name column
        self._player_batting_df = pd.merge(self._player_batting_df, self._names_df, how='inner',on='playerID')
        # drop yearID and rearrange columns
        cols = ['name','playerID','years', 'first_year','last_year','G', 'AB', 'R', 'H', '1B', '2B', '3B', 'HR', 'RBI', 'SB',
               'CS', 'BB', 'SO', 'IBB', 'HBP', 'SH', 'SF', 'GIDP', 'total_bases','AVG','SLG','OBP']
        self._player_batting_df = self._player_batting_df[cols]

    def get_year_in_majors(self, df:pd.DataFrame) ->pd.DataFrame:
        """Add the ordinal year for players in a batting DataFrame
            Arguments:
                df - a DataFrame having the same columns as player_batting_df
            Returns:
                A new DataFrame with a 'year' column added.
        """
        df = df.assign(year=1)
        player_list = df['playerID'].unique()
        year_df = pd.DataFrame(columns=['playerID','yearID'])
        for p in player_list:
            pb_df = df[df['playerID']==p][['playerID','yearID','year']]
            start_year = min(df[df['playerID']==p]['yearID'])
            pb_df['year'] =  pb_df['yearID'].apply(lambda x: x-start_year+1)
            year_df = pd.concat([year_df, pb_df], ignore_index=True)
            pd.concat([year_df, pb_df], ignore_index=True)
    
        df = pd.merge(df, year_df, how='inner',on=['playerID','yearID'])
        df = df.drop(columns= 'year_x')
        df.rename(columns={'year_y':'year'},inplace=True)
        df = df.astype({'year' : 'int32'})
        return df
    
    @property
    def star_player_list(self):
        return self._star_player_list
    
    @property
    def player_batting_df(self):
        return self._player_batting_df
    
    def batting_yearly_stats(self, playerid:str) -> pd.DataFrame:
        # sorted by yearID
        return self.batting_df[self.batting_df['playerID'] == playerid][['yearID','H', '1B','2B','3B','HR','AVG','OBP','SLG']]
    
    def batting_summary_stats(self, playerid:str) -> pd.DataFrame:
        sum_df = self._player_batting_df[self._player_batting_df['playerID'] == playerid]
        return sum_df[['playerID','name','years','H','R','1B','2B','3B','HR','total_bases','AVG','SLG','OBP']]
    
    def get_player_stats(self, batting_df,  player_list) ->pd.DataFrame:
        return batting_df[batting_df['playerID'].isin(player_list)]
        
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--playerID", "-p", help="PlayerID of the player", type=str, default=None)
    parser.add_argument("--summary", "-s", help="Summary stats for a given playerID", action="store_true", default=False)
    parser.add_argument("--format", "-f", help="Output format: json, text, csv", type=str, choices=['csv','json','text'], default='json' )
    args = parser.parse_args()
    
    batting = Batting()
    people_df = batting.people_df
    name = people_df[people_df['playerID'] == args.playerID]['name']
    
    yearly_stats_df = batting.get_player_stats(batting.batting_df, batting.star_player_list)
    player_yearly_stats_df = yearly_stats_df[yearly_stats_df['playerID'] == args.playerID]
    if args.summary:
        playerstats_df = batting.batting_summary_stats(args.playerID)
    else:
        playerstats_df = batting.batting_yearly_stats(args.playerID)
    
    if args.format == 'text':
        print(f'{name} batting stats\n{playerstats_df}')
    elif args.format == 'json':
        result = playerstats_df.to_json(orient="records")
        parsed = json.loads(result)
        print(json.dumps(parsed, indent=4))
    elif args.format == 'csv':
        print(playerstats_df.to_csv(index=False, lineterminator='\n'))
    
    print(player_yearly_stats_df)
    #judge_df = batting.batting_yearly_stats('judgeaa01')
    #print(judge_df)
    #judge_df.plot(x='yearID', y='HR', kind='bar', figsize=(8,4))

    