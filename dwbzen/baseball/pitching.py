'''
Created on Apr 26, 2023

@author: dwbze
'''
import pandas as pd
import argparse
import json
from baseball.databank import BaseballDatabank

class Pitching(BaseballDatabank):
    """
    """

    pitching_db_dict = {
    'playerID': 'Player ID code',
    'yearID': 'Year',
    'stint': 'order of appearances within a season',
    'teamID':'Team',
    'lgID':'League',
    'W' : "Wins",
    'L' : "Losses",
    'G':'Games',
    'GS' : 'Games started',
    'CG' : 'Complete Games',
    'SHO' : 'Shutouts',
    'SV' : 'Saves',
    'GF' : 'Games Finished',
    'R' : 'Runs Allowed'
    }
    
    def __init__(self, start_year=1905, end_year=2022):
        """
        """
        
        super().__init__(start_year, end_year)
        
    def get_complete_games(self, start_year=1950) ->pd.DataFrame:
        completes_df = self._pitching_df[(self._pitching_df['CG'] > 0) & (self._pitching_df['yearID'] >= start_year)]
        completes_df = completes_df[['yearID', 'teamID', 'name', 'CG']]
        return completes_df.sort_values(by=['yearID','name','CG'], ascending=True)
    
    def get_complete_games_by_year(self, start_year=1950) ->pd.DataFrame:
        completes_df = self.get_complete_games(start_year)
        completes_by_year_df = completes_df.groupby(by='yearID').sum(numeric_only=True)
        completes_by_year_df = completes_by_year_df.reset_index()
        completes_by_year_df
    
    def get_player_stats(self, player_id) -> pd.DataFrame:
        if player_id in self._pitching_df['playerID'].values:
            return self._pitching_df[self._pitching_df['playerID']==player_id][['name','playerID', 'yearID','G','GS','GF','CG','SHO']]
        else:
            return pd.DataFrame(columns=['name','playerID','yearID','G','GS','GF','CG','SHO'])
    
    def get_player_summary_stats(self, player_id):
        player_stats = self.get_player_stats(player_id)
        player_summary_stats = player_stats.groupby('name').sum(numeric_only=True)
        player_summary_stats = player_summary_stats.reset_index()
        player_summary_stats = player_summary_stats.assign(years=player_stats.shape[0])
        return player_summary_stats.drop(['yearID'], axis=1)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--playerID", "-p", help="PlayerID of the player", type=str, default=None)
    parser.add_argument("--summary", "-s", help="Summary stats for a given playerID", action="store_true", default=False)
    parser.add_argument("--format", "-f", help="Output format: json, text, csv", type=str, choices=['csv','json','text'], default='json' )
    args = parser.parse_args()

    pitching = Pitching()
    people_df = pitching.people_df
    name = people_df[people_df['playerID'] == args.playerID]['name']
    
    playerstats_df = None
    if args.summary:
        playerstats_df = pitching.get_player_summary_stats(args.playerID)
    else:
        playerstats_df = pitching.get_player_stats(args.playerID)

    if args.format == 'text':
        print(f'{name} pitching stats\n{playerstats_df}')
    elif args.format == 'json':
        result = playerstats_df.to_json(orient="records")
        parsed = json.loads(result)
        print(json.dumps(parsed, indent=4))
    elif args.format == 'csv':
        print(playerstats_df.to_csv(index=False, lineterminator='\n'))
    
    