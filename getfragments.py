#! /usr/bin/python


# TODO: print duration, select search strategy (chronologically), bool shuffle results, store t888 & program info in a database
import json
import os
import re
import sys
import pprint
import random
import time
import argparse
from datetime import timedelta


def parsetimedelta(timestring):
    d = timedelta(hours=int(timestring[0:2]), minutes=int(timestring[3:5]), 
        seconds=int(timestring[6:8]), milliseconds=int(timestring[9:12]))
    return d

def printtimedelta(td):
    return '%02d:%02d:%02d.%03d' % (td.seconds//3600, (td.seconds//60) % 60, td.seconds % 60, td.microseconds/1000)


def convert_to_json(jsonfile):
    # read json file
    jfile = jsonfile.read().split('\n')[0]
    #het is jsonp, dus haal functiecall eraf
    jfile = jfile[14:-2]
    # probeer te laden
    try:
        return json.loads(jfile)
    except:
        print 'invalid json: ' + filename
        return None

def parse_subtitles(programma_json, search_regex, subsfilename, offset=0.0):
    
    # get programma id
    prid = 'undefined'
    if 'prid' in programma_json:
        prid = programma_json['prid']
    pgidsdatum = 'onbekend'
    if 'gidsdatum' in programma_json:
        pgidsdatum = programma_json['gidsdatum']
    if 'titel' in programma_json: print subsfilename, programma_json['titel'],  pgidsdatum

    
    # Walk the subsfile
    prevline = ''
    
    result = []
    
    with open(subsfilename, 'r') as subsfile:
        for line in subsfile:
            # Previous line cannot be empty (should have subtitle timing data), and regex should match
            if not prevline == '' and re.search(search_regex, line):
                # get start and endtime of subtitle
                prevlinesplit = prevline.split(' ')
                starttime = prevlinesplit[0]
                try:
                    endtime = prevlinesplit[2].strip()
                    print '  ' + line,
                    result.append({'prid':prid, 'start_time':starttime, 'end_time':endtime, 'text':line.strip()})
                except:
                    print '  <EXCEPTION>: Unable to read times from string "%s"' %(prevsplit, )
            prevline = line
    # returns a list of dicts, each element is a matching line, each dict has keys 'prid' 'start_time' 'end_time' 'text'
    return result


def main(arguments):
    
    outfile = arguments.output
    subs_folder = arguments.subs
    program_info = arguments.program_info
    program_regex = arguments.program_regex
    search_regex = arguments.search_regex
    shuffle = arguments.shuffle
    start_offset = arguments.offset + arguments.start_padding
    end_offset = arguments.offset + arguments.end_padding
    
    start_time = time.time()

    print "Finding subtitles with expression: %s, in programs with expression %s\nfrom source '%s' to output file '%s'"%(search_regex, program_regex, subs_folder, outfile.name)
    
    # Ga programma's af
    resultlist = []

    for filename in os.listdir(subs_folder):
        programma_json = None
        with open(os.path.join(program_info, filename.split('.')[0] + '.json'), 'r') as jsonfile:
            programma_json = convert_to_json(jsonfile)
        
        if not programma_json is None:
            ptitel = 'onbekend'
            if 'titel' in programma_json:
                ptitel = programma_json['titel']
            # Ignore case, because messy data
            if re.search(program_regex, ptitel, re.IGNORECASE):
                result = parse_subtitles(programma_json, search_regex, os.path.join(subs_folder, filename))
                if not len(result) == 0:
                    resultlist.extend(result)
    
    # sorted_prid = sorted(frequencydict, key=lambda k: len(frequencydict[k]), reverse=True)
    if shuffle:
        random.shuffle(resultlist)
    
    json.dump(resultlist, outfile)
    
    print "Finished in %.0f seconds" % (time.time() - start_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Query the T888 database to find fragments, and build a fragments file from it.')
    parser.add_argument('search_regex', type=str, help='search query')
    parser.add_argument('output', type=argparse.FileType('w'), help='file to save fragments to')
    parser.add_argument('--program_regex', type=str, help='define in which tv program to search', default='.*')
    parser.add_argument('--subs', type=str, help='folder where to search for subtitle files', default='subtitles')
    parser.add_argument('--program_info', type=str, help='folder where to search for program info', default='program_info')
    parser.add_argument('--shuffle', type=bool, default=False, help='toggle shuffling, default is False')
    parser.add_argument('--offset', type=float, default=0.0, help='insert an offset for each subtitle, >0 is later, <0 earlier')
    parser.add_argument('--start_padding', type=float, default=0.0, help='insert a padding to the start of the subtitle, >0 is later, <0 earlier')
    parser.add_argument('--end_padding', type=float, default=0.0, help='insert a padding to the end of the subtitle, >0 is later, <0 earlier')
    
    args = parser.parse_args()

    main(args)
