
import pandas as pd
import pathlib
import json

class Utils(object):
    #
    # breaks up a path name into component parts
    #
    @staticmethod
    def get_file_info(cpath, def_extension='json'):
        known_extensions = [def_extension, 'txt', 'mxl','.xml','musicxml', 'csv']
        x = cpath.split("/")
        paths = x[0:len(x)-1]
        filename = x[-1]
        ext = filename.split(".")
        name = ext[0]
        if len(ext)==2 and ext[1] in known_extensions:
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
    