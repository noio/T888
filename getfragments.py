#! /usr/bin/python


# TODO: print duration, select search strategy (chronologically), bool shuffle results, store t888 & program info in a database
import json
import os
import re
import sys
import pprint
import random
import time

usage = """usage: ./getfragments.py SEARCH_REGEX [PROGRAMMA_REGEX Shuffle output.txt]"""

start_time = time.time()
programmaregex = ".*"
outfile = 'output.txt'
shuffle = False
if len(sys.argv) == 1:
    print usage
    sys.exit()
if len(sys.argv) > 1:
    searchregex = sys.argv[1]
if len(sys.argv) > 2:
    programmaregex = sys.argv[2]
if len(sys.argv) > 3:
    if sys.argv[3] == '1' or sys.argv[3] == 'True':
        shuffle = True
if len(sys.argv) > 4:
    outfile = sys.argv[4]
# programmanaam = programmanaam.lower()
# searchstring = searchstring.lower()

subtitlefolder = 'subtitles/'
pjsonfolder = 'program_info/'

# Ga programma's af
frequencydict = {}

for filename in os.listdir(subtitlefolder):
    if not filename[0] == ".":
        # open subs
        file = open(subtitlefolder + '/' + filename)
        # open json file
        jfile = open(pjsonfolder + '/' + filename.split('.')[0] + '.json').read().split('\n')[0]
        #het is jsonp, dus haal functiecall eraf
        jfile = jfile[14:-2]
        # probeer te laden
        try:
            x = json.loads(jfile)
        except:
            print 'invalid json: ' + filename
            continue
        # get programma id
        prid = 'undefined'
        if 'prid' in x:
            prid = x['prid']
        if 'titel' in x:
            ptitel = x['titel']
            pgidsdatum = 'onbekend'
            if 'gidsdatum' in x:
                pgidsdatum = x['gidsdatum']
            if re.search(programmaregex, ptitel, re.IGNORECASE):
                # Zoek in goede programma
                print filename, ptitel,  pgidsdatum
                prevline = ''
                for line in file:
                    if not prevline == '' and re.search(searchregex, line):
                        if not prid in frequencydict:
                            frequencydict[prid] = []
                        # get start en endtime of subtitle
                        prevsplit = prevline.split(' ')
                        starttime = prevsplit[0]
                        try:
                            endtime = prevsplit[2].strip()
                            print '  ' + line,
                            frequencydict[prid].append([prid, starttime, endtime, line.strip()])
                        except:
                            print '  <EXCEPTION>: Unable to read times from string "%s"' %(prevsplit, )
                        # print filename
                        # print prevline,

                        #print jfile
                        #js = json.loads(jfile)
                    prevline = line

sorted_prid = sorted(frequencydict, key=lambda k: len(frequencydict[k]), reverse=True)
# if topx > 0 and topx < len(frequencydict.items()):
#     print sorted_prid[:topx]
# else :
    # topx = len(frequencydict.items())
    # print sorted_prid
# sorted_prid = sorted_prid[0:1]
print len(sorted_prid)
# print open(pjsonfolder + '/' + sorted_prid[0] + '.json').read()
if shuffle:
    tempfile = outfile
    outfile = '.'.join(outfile.split('.')[:-1] + ['tmp'])
with open(outfile,'w') as resfile:
    for pr in sorted_prid:
        for occurrences in frequencydict[pr]:
            resfile.write(repr(occurrences))
            resfile.write('\n')
if shuffle:
    with open(tmpfile, 'w') as resfile:
        with open(outfile, 'r') as tmp:
            lines = tmp.readlines()
            random.shuffle(lines)
            for line in lines:
                resfile.write(line)
print "Finished in %.0f seconds" % (time.time() - start_time)
# if 'titel' in x:
#     print x['titel']
#     if not x['titel'] in programmadict:
#         programmadict[x['titel']] = 0
#     programmadict[x['titel']] += 1
# pprint.pprint(programmadict)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Query the T888 database to find fragments, and build a fragments file from it.')
#     parser.add_argument('search_regex', type=argparse.String, help='search query')
#     parser.add_argument('program_regex', type=argpase.String, help='define in which tv program to search', default='.*')
#     parser.add_argument('output_file', type=argparse.FileType('w'), help='file to save fragments to', default='output.txt')
#     parser.add_argument('t888_folder', type=argparse.String, help='folder where to search for subtitle files', default='subtitles')
#     
#     args = parser.parse_args()
# 
#     main(args.fragments)
