#! /usr/bin/python

import json
import os
import re
import sys
import pprint
import random

usage = """usage: ./get_kro_subs.py SEARCH_REGEX [PROGRAMMA_REGEX output.txt]"""

programmaregex = ".*"
outfile = 'output.txt'
topx = 1
if len(sys.argv) == 1:
    print usage
    sys.exit()
if len(sys.argv) > 1:
    searchregex = sys.argv[1]
if len(sys.argv) > 2:
    programmaregex = sys.argv[2]
if len(sys.argv) > 3:
    outfile = sys.argv[2]
# programmanaam = programmanaam.lower()
# searchstring = searchstring.lower()

subtitlefolder = 'kro-subtitles/subtitles/'
pjsonfolder = 'kro-subtitles/program_info'


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
            
            if re.search(programmaregex, ptitel, re.IGNORECASE):
                # Zoek in goede programma
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
                        except:
                            print '<EXCEPTION>'
                            endtime = ""
                        # print filename
                        # print prevline,
                        print line,
                        frequencydict[prid].append([prid, starttime, endtime, line.strip()])
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
tmpfile = 'tmp'
with open(tmpfile,'w') as resfile:
    for pr in sorted_prid:
        for occurrences in frequencydict[pr]:
            resfile.write(repr(occurrences))
            resfile.write('\n')
with open(outfile, 'w') as resfile:
    with open(tmpfile, 'r') as tmp:
        lines = tmp.readlines()
        random.shuffle(lines)
        for line in lines:
            resfile.write(line)
        # for fragment in frequencydict[pr]:
        #     resfile.write(fragment)
# if 'titel' in x:
#     print x['titel']
#     if not x['titel'] in programmadict:
#         programmadict[x['titel']] = 0
#     programmadict[x['titel']] += 1
# pprint.pprint(programmadict)