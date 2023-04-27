'''
Created on Apr 22, 2023

@author: dwbzen
'''
import pandas as pd

class BaseballDatabank(object):
    """
        Data from the Lahman baseball database.
    """


    def __init__(self, start_year=1905, end_year=2022):
        """Initialize data files DataFrames
        
        """
        self._start_year = start_year   # modern era
        self._end_year = end_year       # last year there are stats for
        self._resource_base = '/Users/dwbze/OneDrive/Documents/Manuals-Technical/baseball_databases/baseballdatabank-2023.1' 
        self._init_dataframes()

    def _init_dataframes(self):
        """
            Initialize and condition the data. 
        """
        self._teams_df = pd.read_csv(f'{self._resource_base}/core/Teams.csv')
        self._teams_df.sort_values(by='teamID')
        
        self._people_df = pd.read_csv(f'{self._resource_base}/core/People.csv')
        self._people_df  = self._people_df .fillna(0)
        self._people_df['name'] = self._people_df.apply(lambda row: f'{row["nameFirst"]} {row["nameLast"]}', axis=1)
        self._names_df = self._people_df[['playerID', 'name']]
        
        # load and condition batting_df
        self._load_batting()
        # load and condition pitching_df
        self._load_pitching()

        self._appearances_df = pd.read_csv(f'{self._resource_base}/core/Appearances.csv')
        
    def _load_batting(self):
        self._batting_df = pd.read_csv(f'{self._resource_base}/core/Batting.csv')
        # condition the data
        # batting_df is by player & year
        # player_batting_df groups by player & has number of years played
        # star_players is a list of playerIDs for select star players like Ruth & Aaron
        self._batting_df = self._batting_df.fillna(0)
        self._batting_df = self._batting_df[self._batting_df['yearID'] >= self._start_year]
        # eliminate players with fewer than 20 at bats
        self._batting_df = self._batting_df[self._batting_df['AB']>=20]
        
        # for consistency, add singles as '1B'
        singles_df = self._batting_df[['H', '2B','3B','HR']].apply(lambda df: df['H'] - (df['2B'] + df['3B'] + df['HR']), axis=1)
        self._batting_df['1B'] = singles_df
        
        # drop stint and rearrange the columns
        self._batting_df = self._batting_df[['playerID', 'yearID','G', 'AB', 'R', 'H',
        '1B', '2B', '3B', 'HR', 'RBI', 'SB', 'CS', 'BB', 'SO', 'IBB', 'HBP', 'SH',
       'SF', 'GIDP','teamID', 'lgID']]
        
        # add batting average
        batting_averages = self._batting_df[['AB','H']].apply(lambda df: round(df['H']/df['AB'], 3), axis=1)
        self._batting_df['AVG'] = batting_averages

        # on-base percentage
        on_base_percentage = self._batting_df[['AB', 'H', 'HBP', 'BB', 'SF']].\
            apply(lambda df: round(((df['H'] + df['BB'] + df['HBP']) /(df['AB'] +  df['BB'] + df['HBP']+ df['SF'])),3), axis=1) 
        self._batting_df['OBP'] = on_base_percentage
        
        # calculate total bases and slugging percent
        total_bases = self._batting_df[['1B', '2B', '3B', 'HR']].apply(lambda df: round((df['1B'] + 2*df['2B'] + 3*df['3B'] + 4*df['HR']),3),axis=1 )
        self._batting_df['total_bases'] = total_bases
        SLG = self._batting_df[['total_bases', 'AB']].apply(lambda df: round((df['total_bases'])/df['AB'],3),axis=1 )
        self._batting_df['SLG'] = SLG
        
        # merge with players (people_df) to create a name column nameFirst + nameLast
        self._batting_df = pd.merge(self._batting_df, self._names_df, how='inner',on='playerID')
        
    def _load_pitching(self):
        self._pitching_df = pd.read_csv(f'{self._resource_base}/core/Pitching.csv')
        self._pitching_df = self._pitching_df.fillna(0)
        self._pitching_df = self._pitching_df[self._pitching_df['yearID'] >= self._start_year]
        
        # merge with players (people_df) to create a name column nameFirst + nameLast
        
        self._pitching_df = pd.merge(self._pitching_df, self._names_df, how='inner',on='playerID')

    
    @property
    def resource_folder(self):
        return self._resource_base
    
    @property
    def end_year(self):
        return self._end_year
    
    @property
    def start_year(self):
        return self._start_year
    
    @property
    def teams_df(self):
        return self._teams_df
    @property
    def batting_df(self):
        return self._batting_df
    @property
    def pitching_df(self):
        return self._pitching_df
    @property
    def people_df(self):
        return self._people_df
    @property
    def appearances_df(self):
        return self._appearances_df
    @property
    def names_df(self):
        return self._names_df
    
if __name__ == '__main__':
    databank = BaseballDatabank(1905, 2022)
    batting_df = databank.batting_df
    
    print(batting_df[batting_df['playerID'] == 'ruthba01'])
    
