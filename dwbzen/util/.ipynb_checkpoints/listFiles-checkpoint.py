'''
Created on Sep 7, 2025

@author: don_bacon
'''

from pathlib import Path
import argparse
import json
import re

RE2 = re.compile(r'(.+)\s+-\s+(.+).[mM][pP]3')
RE3 = re.compile(r'(.+)\s+-\s+(.+).m4A')    # add more as needed
RE1 = re.compile(r'^\d\d[ _]+(.+)\s+-\s+(.+).mp3')
MATCH_PATTERNS = [RE1, RE2, RE3]

def split_name(filename:str)->tuple[str,str]:
    """Make a reasonable attempt at splitting a music file name
        into component artist and title
        Returns a 2-element tuple (artist, title)
    """
    for pattern in MATCH_PATTERNS:
        _match = pattern.match(filename)
        if _match is not None and len(_match.groups()) == 2:
            artist = _match.group(1)
            name = _match.group(2)
            break
    else:
        artist = ""
        name = filename

    return artist,name

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="listFiles", description="List files and folders from a given path.", usage="%(prog)s [options]")
    parser.add_argument("--path", "-P", help="Starting path folder", type=str, default=".")    # for example: "F:/Music/MP3", default is current folder
    parser.add_argument("--format", help="Output format: text or json", type=str, choices=['text','json'], default='text')
    parser.add_argument("--filter", "-F", help="List of file extensions to match, for example '*.txt' ", type=str, default="*")    # ,delimited list
    parser.add_argument("--music", "-M", help="List only music files '*.mp3, *.m4a' ", action="store_true", default=False)
    parser.add_argument("--names", "-N", help="Display only the file names, default is display the entire path", action="store_true", default=False)
    parser.add_argument("--dir", "-D", help="Include folders in the output list, default is not to include", action="store_true", default=False)
    parser.add_argument("--count", "-C", help="Provide a count of files only: total and by folder", action="store_true", default=False)
    parser.add_argument("--sort", "-S", help="Sort the output by folder/name", action="store_true", default=False)
    parser.add_argument("--list", "-L", help="Display as a List, default is False", action="store_true", default=False)
    parser.add_argument("--save", "-s", help="Save to the designated file", type=str, default=None)    # can also redirect output 
    args = parser.parse_args()
    
    base_path = Path(args.path)
    # list the directories
    directories = []
    for child in base_path.iterdir():
        if child.is_dir():
            directories.append(child)
    directory_files = {}    # key is directory name, value is list of filenames in that directory
    counts = {}    # key is directory name, value is number of files in that path
    total_count = 0
    _filter = "*.m[p4][3aA]" if args.music else args.filter
    for i,dir_path in enumerate(directories):
        files_list = []
        for path in dir_path.rglob(_filter):
            fname = path.name if args.names else str(path)
            files_list.append(fname)
        if args.sort: files_list.sort()    # sort the list in place
        directory_files[dir_path.name] = files_list
        fcount = len(files_list)
        counts[dir_path.name] = fcount
        total_count += fcount
    
    # list by directory
    _dict = {}
    for i,dir_path in enumerate(directories):
        files_list = directory_files[dir_path.name]
        if args.format == "text":
            dir_name = dir_path.name
            if args.dir:
                print(f"{i+1}. {dir_name}, count: {counts[dir_name]}:")
            if args.list:
                print(files_list)
            else:
                if not args.count:
                    for name in files_list: print(f"  {name}")

        elif args.format == "json":
            dlist = []
            for n,name in enumerate(files_list):
                if args.names and args.music:    # split the name into artist,title
                    artist,title = split_name(name)
                    if not title.endswith("jpg"):
                        dlist.append({"number": n, "artist" : artist, "title" : title})
                else:
                    dlist.append({"number": n, "name" : name})
            _dict[dir_path.name] = dlist
        else:    # unknown format
            print(files_list)
            
    if args.count and args.format == "text":
        print(f"Total count: {total_count}")
        
    if args.format == "json":
        print(json.dumps(_dict, indent=2))

        