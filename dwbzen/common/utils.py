# ------------------------------------------------------------------------------
# Name:          utils.py
# Purpose:       Common utilities.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon

# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import pathlib
import json
import math
from datetime import datetime

class Utils(object):
    
    known_extensions = ['json', 'txt', 'mxl', 'xml', 'musicxml', 'csv']

    @staticmethod
    def get_file_info(cpath, def_extension='json'):
        """breaks up a path name into component parts
        
        """
        
        x = cpath.split("/")
        paths = x[0:len(x)-1]
        filename = x[-1]
        ext = filename.split(".")       # name.extension as in "foo.csv"
        name = ext[0]
        if len(ext)==2 and ext[1] in Utils.known_extensions:
            ext = ext[1]
            path = cpath      
        else:
            ext = def_extension
            filename = f"{filename}.{ext}"
            path = f"{cpath}.{ext}"
        p = pathlib.Path(path)
        exists = p.exists()
        return  {'paths':paths, 'path_text':path, 'filename':filename, 'name':name,'extension': ext, 'Path':p, 'exists':exists}


    @staticmethod
    def round_values(x, places=5):
        if not type(x) is str:
            return round(x, places)
        else:
            return x
    
    @staticmethod
    def get_json_output(df, orient='index'):
        """Dumps the dataframe argument to a nicely formated text string.
        
        """
        result = df.to_json(orient=orient)
        parsed = json.loads(result)
        return json.dumps(parsed, indent=4)
    
    @staticmethod
    def time_since(base_date:datetime=datetime(2000, 1, 1, 0, 0),  end_date=datetime.now(), what='seconds') -> int:
        """Gets the elapsed seconds or days between two given base date/datetime
            Arguments:
                base_date : the base date, default is 12:00 AM 2000-01-01
                end_date : the ending date/datetime, default is now()
                what : 'seconds' or 'days'
            Returns:
                The seconds or days since the base date to end_date as an integer
            Note - useful in setting a random seed as in random.seed(time_since())
        """
        
        delta = end_date-base_date
        if what=='seconds':
            return math.trunc(delta.total_seconds())
        else:   # assume days
            return delta.days
        
if __name__ == '__main__':
    print(Utils.__doc__)
    