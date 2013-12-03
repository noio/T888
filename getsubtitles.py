#!/usr/bin/env python

""" Scraper for T888 subtitle data from the npo/uitzendingemist site
"""

# Dit is nog geen scraper ^^ ^^.
#import os
#os.system("mkdir kro-subtitles")
#os.system("curl -0 http://www.hackdeoverheid.nl/wp-content/uploads/sites/10/2013/11/kro-subtitles.zip | tar -zx -C subtitles")


# basis url: http://e.omroep.nl/tt888/prid

# Dit is ook geen scraper =D
# bron uitleg: http://www.hackdeoverheid.nl/datablog-programma-omschrijvingen/

import os, sys, shutil
def main():
    prid_source = "http://www.hackdeoverheid.nl/wp-content/uploads/sites/10/2013/11/all-prids-only1.zip"
    t888_source = "http://e.omroep.nl/tt888"
    src_folder = "program_info"
    destination_folder = "subtitles"
    
    if not os.path.exists(src_folder):
        # extracts to folder 'program_info
        os.system("curl -0 %s | tar -zx" % (prid_source, ))
    
    if not os.path.exists(destination_folder):
        os.mkdir(destination_folder)
    
    files = os.listdir(src_folder)
    
    no_subs = 0
    no_files = 0
    for file in files:
        if not file[0] == '.':
            no_files += 1
            prid = file.split('.')[0]
            print prid
            # Save subs
            dest_path = "%s/%s.txt"%(destination_folder, prid)
            os.system("curl -0 -s %s/%s > %s"% (t888_source, prid, dest_path))
            string = open(dest_path, 'r').read()
            if string == "No subtitle found":
                # If file only contains no subtitle found' remove it
                os.remove(dest_path)
            else:
                no_subs += 1
    print "Subtitles saved: %d"% (no_subs,)
    print "Programs searched: %d"%(no_files,)

if __name__ == '__main__':
    main()
