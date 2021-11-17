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
    def get_json_output(df):
        """Dumps the dataframe argument to a nicely formated text string.
        
        """
        result = df.to_json(orient='index')
        parsed = json.loads(result)
        return json.dumps(parsed, indent=4)
    
    if __name__ == '__main__':
        print(Utils.__doc__)
    