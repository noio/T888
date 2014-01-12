#! /usr/bin/python


# TODO: print duration, select search strategy (chronologically), bool shuffle results, store t888 & program info in a database
import json
import os
import re
import random
import time
import argparse
from datetime import timedelta

### CONSTANTS ###

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
        print 'invalid json: ' + jsonfile.name
        return None

def parse_subtitles(programma_json, search_regex, subsfilename, match_only=False, offset=0.0, verbose=False):
    
    # get programma id
    prid = 'undefined'
    if 'prid' in programma_json:
        prid = programma_json['prid']
    pgidsdatum = ''
    if 'gidsdatum' in programma_json:
        pgidsdatum = programma_json['gidsdatum']
    
    if 'titel' in programma_json:
        if verbose:
            print subsfilename, programma_json['titel'],  pgidsdatum
    
    streamSense_program = ''
    if 'streamSense' in programma_json:
        if 'program' in programma_json['streamSense']:
            streamSense_program = programma_json['streamSense']['program']
    # Walk the subsfile
    prevline = ''
    
    result = []
        
    if (os.path.exists(subsfilename)):
        with open(subsfilename, 'r') as subsfile:
            for line in subsfile:
                # Previous line cannot be empty (should have subtitle timing data), and regex should match
                if not prevline == '' and re.search(search_regex, line):
                    # get start and endtime of subtitle
                    prevlinesplit = prevline.split(' ')
                    starttime = prevlinesplit[0]
                    if not match_only:
                        text = line.strip()
                    else:
                        text = re.search(search_regex, line).group().strip()

                    try:
                        endtime = prevlinesplit[2].strip()
                        if verbose: print line,
                        result.append({'prid':prid, 'start_time':starttime, 'end_time':endtime, 'text':text, 'gidsdatum':pgidsdatum, 'streamSense_program':streamSense_program})
                    except:
                        print '  <EXCEPTION>: Unable to read times from string "%s"' %(prevlinesplit, )
                prevline = line
        # returns a list of dicts, each element is a matching line, each dict has keys 'prid' 'start_time' 'end_time' 'text'
        return result


def main(outfile,
         subs_folder,
         program_info,
         program_regex,
         search_regex,
         shuffle,
         start_offset,
         end_offset,
         match_only,
         verbose):
    
    start_time = time.time()

    print 'Finding subtitles matching "%s", in programs matching "%s"\nfrom source <%s> to output file <%s>' % (search_regex, program_regex, subs_folder, outfile)
    
    # Ga programma's af
    resultlist = []

    for filename in os.listdir(subs_folder):
        programma_json = None
        try:
            with open(os.path.join(program_info, filename.split('.')[0] + '.json'), 'r') as jsonfile:
                programma_json = convert_to_json(jsonfile)
        except IOError:
            print "Couldn't find or open " + os.path.join(program_info, filename.split('.')[0] + '.json')
            continue
        
        if not programma_json is None:
            ptitel = 'onbekend'
            if 'titel' in programma_json:
                ptitel = unicode(programma_json['titel'])
            # Ignore case, because messy data
            if re.search(program_regex, ptitel, re.IGNORECASE):
                result = parse_subtitles(programma_json, search_regex, os.path.join(subs_folder, filename), 
                    match_only=match_only, verbose=verbose)
                if result:
                    resultlist.extend(result)
    
    # sorted_prid = sorted(frequencydict, key=lambda k: len(frequencydict[k]), reverse=True)
    if shuffle:
        random.shuffle(resultlist)
    
    json.dump(resultlist, open(outfile, 'w'), indent=2)
    
    print "Found %d clips." % len(resultlist)
    print "Finished in %.0f seconds" % (time.time() - start_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Query the T888 database to find fragments, and build a fragments file from it.')
    parser.add_argument('search_regex', type=str, help='search query')
    parser.add_argument('output', type=str, help='file to save fragments to')
    parser.add_argument('--program_regex', '-p', type=str, help='define in which tv program to search', default='.*')
    parser.add_argument('--subs', type=str, help='folder where to search for subtitle files', default='subtitles')
    parser.add_argument('--program_info', type=str, help='folder where to search for program info', default='program_info')
    parser.add_argument('--shuffle', action='store_true', default=False, help='Shuffle the clips.')
    parser.add_argument('--offset', type=float, default=0.0, help='insert an offset for each subtitle, >0 is later, <0 earlier')
    parser.add_argument('--start_padding', type=float, default=0.0, help='insert a padding to the start of the subtitle, >0 is later, <0 earlier')
    parser.add_argument('--end_padding', type=float, default=0.0, help='insert a padding to the end of the subtitle, >0 is later, <0 earlier')
    parser.add_argument('--match_only', '-m', action='store_true', default=False, help='Include only the matching part of the regex.')    
    parser.add_argument('--verbose', '-v', action='store_true', default=False, help='Print more info.')    

    args = parser.parse_args()

    main(args.output,
         args.subs,
         args.program_info,
         args.program_regex,
         args.search_regex,
         args.shuffle,
         args.offset + args.start_padding,
         args.offset + args.end_padding,
         args.match_only,
         args.verbose)
