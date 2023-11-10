'''
Created on Apr 22, 2023

@author: dwbzen
'''

import argparse
import pandas as pd
from baseball.databank import BaseballDatabank

class RetroSheet(object):
    """
    retrosheet.org
    """

    all_column_names = 'date,game_number,day,visiting_team,visiting_team_league,visiting_team_game_number,home_team,home_team_league,\
home_team_game_number,visiting_team_score,home_team_score,game_outs,day_night,completion_info,forfeit_info,protest_info,park_id,\
attendance,game_minutes,visiting_team_line_score,home_team_line_score,visitor_at_bats,\
visitor_singles,visitor_doubles,visitor_tripples,visitor_homers,\
visitor_rbi,visitor_sac_hits,visitor_sac_flies,visitor_hit_by_pitch,visitor_walks,visitor_int_walks,visitor_kos,\
visitor_stolen_bases,visitor_caught_stealing,visitor_dp,visitor_awarded_first,visitor_lob,visitor_pitchers_used,\
visitor_earned_runs,visitor_team_earned_runs,visitor_wild_pitches,visitor_balks,visitor_put_outs,visitor_assists,visitor_errors,\
visitor_passed_balls,visitor_double_plays,visitor_triple_plays,home_at_bats,\
home_singles,home_doubles,home_triples,home_homers,\
home_rbi,home_sac_hits,home_sac_flies,home_hit_by_pitch,home_walks,home_int_walks,home_kos,home_stolen_bases,home_caught_stealing,home_dp,\
home_awarded_first,home_lob,home_pitchers_used,home_earned_runs,home_team_earned_runs,home_wild_pitches,home_balks,\
home_put_outs,home_assists,home_errors,home_passed_balls,home_double_plays,home_triple_plays,\
umpier_id_home,umpire_name_home,umpire_id_1b,umpire_name_1b,umpire_id_2b,umpire_name_2b,umpire_id_3b,umpire_name_3b,\
umpire_id_lf,umpire_name_lf,umpire_id_rf,umpire_name_rf,\
visitor_manager_id,visitor_manager_name,home_manager_id,home_manager_name,\
winning_pitcher_id,winning_pitcher_name,losing_pitcher_id,losing_pircher_name,saving_pitcher_id,saving_pitcher_name,\
winning_rbi_batter_id,winning_rbi_batter_name,visitor_starting_pitcher_id,visitor_starting_pitcher_name,\
home_starting_pitcher_id,home_starting_pitcher_name,visitor_player_id_01,visitor_player_name_01,visitor_player_position_01,\
visitor_player_id_02,visitor_player_name_02,visitor_player_position_02,\
visitor_player_id_03,visitor_player_name_03,visitor_player_position_03,\
visitor_player_id_04,visitor_player_name_04,visitor_player_position_04,\
visitor_player_id_05,visitor_player_name_05,visitor_player_position_05,\
visitor_player_id_06,visitor_player_name_06,visitor_player_position_06,\
visitor_player_id_07,visitor_player_name_07,visitor_player_position_07,\
visitor_player_id_08,visitor_player_name_08,visitor_player_position_08,\
visitor_player_id_09,visitor_player_name_09,visitor_player_position_09,\
home_player_id_01,home_player_name_01,home_player_position_01,home_player_id_02,home_player_name_02,home_player_position_02,home_player_id_03,home_player_name_03,home_player_position_03,home_player_id_04,home_player_name_04,home_player_position_04,home_player_id_05,home_player_name_05,home_player_position_05,home_player_id_06,home_player_name_06,home_player_position_06,home_player_id_07,home_player_name_07,home_player_position_07,home_player_id_08,home_player_name_08,home_player_position_08,home_player_id_09,home_player_name_09,home_player_position_09,additional_info,acquisition_info'

    def __init__(self, start_year=1905, end_year=2022):
        """Initialize data files DataFrames
        
        """
        self.baseball_databank = BaseballDatabank(start_year=start_year, end_year=end_year)
        self._resource_base = '/Users/dwbze/OneDrive/Documents/Manuals-Technical/baseball_databases/retrosheet.org' 

        self.start_year = start_year
        self.end_year = end_year
        
        self.batting_df = self.baseball_databank.batting_df
        self.people_df = self.baseball_databank.people_df
        self.teams_df = self.baseball_databank.teams_df
        self.appearances_df = self.baseball_databank.appearances_df
        
        # Teams_League.csv is created from retrosheet.org file  TEAMABR.txt, adding a 'name' column
        self.teams_league_df = pd.read_csv(f'{self._resource_base}/Teams_League.csv')
        
        self._cols = ['date', 'visiting_team','visiting_team_score','home_team','home_team_score']
        self._all_cols = ['date', 'year', 'visiting_team','visiting_team_score','home_team','home_team_score', 'winning_team', 'losing_team']
        self._game_scores_df = self._load_games(start_year, end_year)
        
        self._teams_df = pd.read_csv(f'{self._resource_base}/core/Teams.csv')
        self._teams_df = self._teams_df.sort_values(by='teamID')
    
    def _load_games(self, start_year, end_year):
        file_base = f'{self._resource_base}/game logs/GL'
        games_df = pd.DataFrame(columns=self._cols)
        for year in range(start_year, end_year+1):
            filename = '{}{}.csv'.format(file_base,year)
            if(year == start_year):
                games_df =  pd.read_csv(filename)
            else:
                gl_df = pd.read_csv(filename)
                games_df = pd.concat([games_df, gl_df], ignore_index=True)
        year_ser = (games_df['date']/10000).astype(int)
        games_df['year'] = year_ser
        wt_ser = games_df[['visiting_team','visiting_team_score','home_team','home_team_score']].apply(lambda df: RetroSheet.get_winning_team(df), axis=1)
        games_df['winning_team'] = wt_ser
        lt_ser = games_df[['visiting_team','visiting_team_score','home_team','home_team_score']].apply(lambda df: RetroSheet.get_losing_team(df), axis=1)
        games_df['losing_team'] = lt_ser
        return games_df[self._all_cols]
    
    @staticmethod
    def get_winning_team(df:pd.DataFrame)->str:
        winning_team = ''
        if(df['visiting_team_score'] > df['home_team_score']):
            winning_team = df['visiting_team']
        else:
            winning_team = df['home_team']
        return winning_team
    
    @staticmethod
    def get_losing_team(df:pd.DataFrame)->str:
        losing_team = ''
        if(df['visiting_team_score'] > df['home_team_score']):
            losing_team = df['home_team']
        else:
            losing_team = df['visiting_team']
        return losing_team    
    
    @property
    def get_resource_folder(self):
        return self._resource_base
    
    @property
    def game_scores_df(self)->pd.DataFrame:
        return self._game_scores_df
    
    @property
    def teams_df(self):
        return self._teams_df
    
    def get_team_IDs_for_years(self, start_year=1905):
        teams_df = pd.read_csv(f'{self._resource_base}/Teams_League.csv')
        teams_df.fillna(value= {'lgID':'NA'}, inplace=True)
        teams_df = teams_df[teams_df['end_year'] >= start_year][['teamID','name','lgID','city','nickname']]
        teams_df = teams_df.set_index(['teamID','lgID'], drop=False)
        return teams_df
    
    def get_teamIDs_Rank(self, start_year=1905):
        columns = ['yearID','lgID','divID','teamID', 'name', 'Rank', 'DivWin', 'WCWin', 'LgWin', 'WSWin']
        teams_rank_df = pd.read_csv(f'{self._resource_base}/core/Teams.csv')
        teams_rank_df = teams_rank_df[teams_rank_df['yearID'] >= start_year][columns]
        teams_rank_df.fillna(value= {'lgID':'NA', 'divID':'NA'}, inplace=True)
        teams_rank_df.fillna(value={'DivWin':0, 'LgWin':0, 'WCWin':0, 'WSWin':0}, inplace=True)
        return teams_rank_df
    
    #
    # compute winning and losing streaks of teams by year
    #
    #game_scores_team_df.iloc[0]['winning_streak']
    #years = game_scores_df['year'].unique()
    #teams = game_scores_df['visiting_team'].append(game_scores_df['home_team']).unique()
    #
    def compute_streak(self, team, year):
        """
        This fills in the winning_streak and losing_streak columns of self._game_scores_df
        Arguments:
            team - team code as in 'NYA' for example
            year - the desired year
        Returns:
            A DataFrame with the columns year, winning_team, losing_team, winning_streak, losing_streak
                there is one row for each game played by the designated team.
                winning_streak is a count of consecutive wins, losing_streak is a count of consecutive losses.
                For a 162 game regular seasons, there would be 162 rows.
        """
        game_scores_team_df = \
          self._game_scores_df[((self._game_scores_df['visiting_team']==team) | (self._game_scores_df['home_team']==team)) & \
          (self._game_scores_df['year']==year)]
        if(len(game_scores_team_df) == 0):
            streak_df = pd.DataFrame(columns = ['year','date','winning_team','losing_team','winning_streak','losing_streak'])
            return game_scores_team_df,streak_df
        #
        # do row 0 first
        #
        prev_row = 0
    
        data = game_scores_team_df.iloc[0][['year','winning_team','losing_team']]
        streak_df = pd.DataFrame(data=data.to_dict(), index=[0] )
    
        if(data['winning_team'] == team):
            streak_df = streak_df.assign(winning_streak=1, losing_streak=0)
        else:
            streak_df = streak_df.assign(winning_streak=0, losing_streak=1)
        #
        # iterate over the remaining rows
        #
        for row in range(1,len(game_scores_team_df)):
            data = game_scores_team_df.iloc[row][['year','winning_team','losing_team']]
            prow = streak_df.iloc[prev_row]
            srow_df = pd.DataFrame(data=data.to_dict(), index=[row] )
            
            if(data['winning_team'] == team):
                ws = prow['winning_streak'] + 1
                srow_df = srow_df.assign(winning_streak=ws, losing_streak=0)
            else:
                ls = prow['losing_streak'] + 1
                srow_df = srow_df.assign(winning_streak=0, losing_streak=ls)
    
            streak_df = pd.concat([streak_df, srow_df], ignore_index=True)
            prev_row = row
            
        return game_scores_team_df, streak_df

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--teamID", help="3-character teamID of the team, for example 'NYA' for the Yankees", type=str, default=None)
    parser.add_argument("--year","-y", help="Year of the desired season", type=int, default=2022)
    parser.add_argument("--summary", "-s", help="Summary stats for a given playerID", action="store_true", default=False)
    parser.add_argument("--format", "-f", help="Output format: json, text, csv", type=str, choices=['csv','json','text'], default='text' )
    args = parser.parse_args()

    teamID = args.teamID
    year = args.year
    retroSheet = RetroSheet(start_year=2021, end_year=2022)
    game_scores_team_df, streak_df = retroSheet.compute_streak(teamID, year)
    
    print(streak_df)
    
    