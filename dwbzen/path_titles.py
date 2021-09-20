'''
Created on Apr 10, 2021

@author: don_bacon
'''
import fileinput, taglib, argparse, re, os
from sys import __stderr__

class Path_titles(object):
    
    def __init__(self, file_name='', matchPath=''):
        '''
        Constructor
        '''
        self.filename = file_name
        self.count = 0
        self.renamedCount = 0
        self.verbose = 0
        self.list=False
        self.errors = []
        self.noArtist = []
        self.matchPatterns = []
        self.matchPath = matchPath
        self.rename = False     # if true, replace the matching text with the ARTIST name in the filename
        self.delete = False     # if true, delete the matching text from the filename and rename
        self.verify = False
        
    def save_match_patterns(self, patterns:list):
        '''
        patterns is a list of compiled regular expressions
        '''
        for pattern in patterns:
            self.matchPatterns.append(re.compile(pattern, re.IGNORECASE))
    
    def process_line(self, line: str) -> tuple:
        parts = line.rsplit('/')
        n = len(parts)
        filename = parts[n-1]
        path = '/'.join(parts[0:n-1])
        if(path.startswith('./')):
            path = path.lstrip('.')
        return (path, filename)
    
    def rename_file(self, oldfile_path:str,  newfile_path:str) -> bool:
        try:
            os.rename(oldfile_path, newfile_path)
            return True
        except OSError as err:
            self.errors.append(oldfile_path)
            print('OSError: Could not rename file: "{}"  because \n\t{}'.format(oldfile_path, err.strerror), file=__stderr__)
            return False
    
    def process_file(self):
        audioFilename = ''
        with fileinput.input(files=self.filename) as f:
            for line in f:
                if(self.verbose >= 2):
                    print('line: {}'.format(line))
                (path, filename) = self.process_line(line)
                if(self.matchPath is not None and path.find(self.matchPath) < 0):
                    continue
                filename=filename.rsplit('\n')
                if(self.verbose > 2):
                    print("{p}\t{f}".format(p=path, f=filename))
                try:
                    audioFilename = filename[0]
                    filepath =  path + "/" + audioFilename
                    song=taglib.File(filepath)
                except OSError:
                    self.errors.append(filepath)
                    print('Could not read file: {}'.format(filepath), file=__stderr__)
                    continue
                if('ARTIST' in song.tags):
                    artists = song.tags['ARTIST']   # returns a list of artists delimited by slash "/"
                    song.close()
                    artist = ','.join(artists)
                    artist = artist.replace('/', ',')       # replace '/' delimiter with a comma
                    if(self.list):
                        print('{}\t{}'.format(artist, filepath))
                    if(self.rename or self.delete):
                        # rename the file, replacing the matched portion of the filename with the ARTIST tag 
                        # if delete is true, delete the matching portion from the filename
                        #
                        for regx in self.matchPatterns:
                            matchit = regx.match(audioFilename)
                            if(matchit is not None):
                                if(self.rename):
                                    new_audioFilename = '{} - {}'.format(artist, audioFilename[matchit.end()+1:])
                                elif(self.delete):
                                    new_audioFilename = audioFilename[matchit.end():]
                                new_audioFile_path = '{}/{}'.format(path, new_audioFilename)
                                if(self.verbose >0):
                                    print('\t match on "{}" start,end {}, {}'.format(audioFilename,matchit.start(), matchit.end()))
                                if(self.verify):
                                    answer = input('\t Rename "{}" to "{}" ? (y/n/q): '.format(audioFilename, new_audioFilename)).rstrip().lower()
                                    if 'y' == answer:
                                        renamed = self.rename_file(filepath, new_audioFile_path)
                                        if renamed:
                                            print("\t file renamed to {}".format(new_audioFilename))
                                            self.renamedCount = self.renamedCount + 1
                                        else:
                                            print("\t unable to rename to {}".format(new_audioFilename), file=__stderr__)
                                    elif 'n' == answer:
                                        print('{} not renamed'.format(audioFilename))
                                    elif 'q' == answer:
                                        return
                                else:
                                    renamed = self.rename_file(filepath, new_audioFile_path)
                                    if renamed:
                                        print("\t file renamed to {}".format(new_audioFilename))
                                        self.renamedCount = self.renamedCount + 1
                                    else:
                                        print("\t unable to rename to {}".format(new_audioFilename), file=__stderr__)
                else:
                    self.noArtist.append(filepath)
                    song.close()
                self.count = self.count + 1
        return self.count


    def getArtist(self):
        pass
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process audio files.')
    parser.add_argument('file',  help='text file of audio file path(s).')
    parser.add_argument('--path', help='audio files match path.')
    parser.add_argument('--list', '-l', action='store_true', help='print artists and titles of songs')
    parser.add_argument('--rename', action='store_true', help='rename file if name matches one of the patterns')
    parser.add_argument('--delete', action='store_true', help='delete the matching string from the file name matches one of the patterns')
    parser.add_argument('--verify', action='store_true', help='verify file rename')    
    parser.add_argument('--patterns', default='\d\d-\d\d-', help='filename matching pattern regular expression(s)' )
    parser.add_argument('--verbose', '-v', action='count', default=0, help='verbose output level')
    
    args = parser.parse_args() 
    filename=args.file
    path = args.path
    if(args.delete and args.rename):
        print("You can't both rename the file and delete the prefix", end='\n', file=__stderr__)
        exit()

    pathTitles = Path_titles(filename)
    pathTitles.matchPath = path
    pathTitles.verbose = args.verbose
    pathTitles.list = args.list
    pathTitles.rename = args.rename
    pathTitles.delete = args.delete
    pathTitles.verify = args.verify
    pathTitles.save_match_patterns(args.patterns.split(','))
    count = pathTitles.process_file()
    print("number of titles: {}".format(count))
    print('{} files renamed'.format(pathTitles.renamedCount))
    if(len(pathTitles.noArtist) > 0):
        print('the following {} titles have no artist'.format(len(pathTitles)))
        for s in pathTitles.noArtist:
            print(s)
    
    