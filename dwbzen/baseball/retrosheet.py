'''
Created on Apr 22, 2023

@author: dwbzen
'''

import numpy as np
import pandas as pd
from .databank import BaseballDatabank

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
winning_rbi_batter_id,winning_rbi_batter_name,visitor_starting_pitcher_id,visitor_starting_pitcher_name,home_starting_pitcher_id,home_starting_pitcher_name,visitor_player_id_01,visitor_player_name_01,visitor_player_position_01,visitor_player_id_02,visitor_player_name_02,visitor_player_position_02,visitor_player_id_03,visitor_player_name_03,visitor_player_position_03,visitor_player_id_04,visitor_player_name_04,visitor_player_position_04,visitor_player_id_05,visitor_player_name_05,visitor_player_position_05,visitor_player_id_06,visitor_player_name_06,visitor_player_position_06,visitor_player_id_07,visitor_player_name_07,visitor_player_position_07,visitor_player_id_08,visitor_player_name_08,visitor_player_position_08,visitor_player_id_09,visitor_player_name_09,visitor_player_position_09,home_player_id_01,home_player_name_01,home_player_position_01,home_player_id_02,home_player_name_02,home_player_position_02,home_player_id_03,home_player_name_03,home_player_position_03,home_player_id_04,home_player_name_04,home_player_position_04,home_player_id_05,home_player_name_05,home_player_position_05,home_player_id_06,home_player_name_06,home_player_position_06,home_player_id_07,home_player_name_07,home_player_position_07,home_player_id_08,home_player_name_08,home_player_position_08,home_player_id_09,home_player_name_09,home_player_position_09,additional_info,acquisition_info'

    def __init__(self):
        """Initialize data files DataFrames
        
        """
        self.baseball_databank = BaseballDatabank()
        self._resource_base = '/Users/dwbze/OneDrive/Documents/Manuals-Technical/baseball_databases/retrosheet.org' 

        self.start_year = self.baseball_databank.start_year
        self.end_year = self.baseball_databank.end_year
        
        self.batting_df = self.baseball_databank.batting_df
        self.people_df = self.baseball_databank.people_df
        self.teams_df = self.baseball_databank.teams_df
        self.appearances_df = self.baseball_databank.appearances_df
        
        # Teams_League.csv is created from retrosheet.org file  TEAMABR.txt, adding a 'name' column
        self.teams_league_df = pd.read_csv(f'{self.resource_base}/Teams_League.csv')
    
    @property
    def get_resource_folder(self):
        return self._resource_base
    
    
    