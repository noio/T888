#!/usr/bin/env python

import argparse
import json
from datetime import datetime, timedelta
import os
import platform
import shutil
from glob import glob
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException

### CONSTANTS ###
MAX_CHARACTERS_PER_SUBTITLE_LINE = 25
USER_AGENT_STRING = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.30.1 (KHTML, like Gecko) Version/6.0.5 Safari/536.30.1"
CACHE = 'cache'

if platform.system() == 'Darwin':
    CHROME_OPTIONS = ["--user-agent="+USER_AGENT_STRING, "--disable-extensions", "--disable-bundled-ppapi-flash", "--disable-internal-flash"] 
    VIDTOOL = 'ffmpeg'
    USE_MENCODER = False
else:
    CHROME_OPTIONS = ["--user-data-dir=/home/sicco/.config/chromium/Default" ,"--user-agent="+USER_AGENT_STRING, "--disable-extensions", "--disable-bundled-ppapi-flash", "--disable-internal-flash"] 
    VIDTOOL = 'avconv'
    USE_MENCODER = True

### FUNCTIONS ###

def fragmenturl(obj):

    pr_id = obj['prid']
    pr_date = obj['gidsdatum']
    pr_date2 = "{}-{}-{}".format(pr_date[8:10], pr_date[5:7], pr_date[:4])
    pr_titel = obj['streamSense_program'].replace('_','-')

    return "http://www.npo.nl/{}/{}/{}".format(pr_titel, pr_date2, pr_id)

def parsetimedelta(timestring):
    d = timedelta(hours=int(timestring[0:2]), minutes=int(timestring[3:5]), 
        seconds=int(timestring[6:8]), milliseconds=int(timestring[9:12]))
    return d

def printtimedelta(td):
    return '%02d:%02d:%02d.%03d' % (td.seconds//3600, (td.seconds//60) % 60, td.seconds % 60, td.microseconds/1000)

def subtitle(inp):
    inp = inp.replace(':','')
    inp = inp.replace('"', '')
    inp = inp.replace("'", '')
    words = inp.split(' ')
    lines = []
    for word in words:
        if lines and len(lines[-1]) + len(word) < MAX_CHARACTERS_PER_SUBTITLE_LINE:
            lines[-1] += ' ' + word
        else:
            lines.append(word)

    return '\n'.join(lines)

def download(vidurl, outputfile, starttime=None, timespan=None, text=None, use_cache=True):
    """ Saves a video for a given npo.nl url, using ffmpeg
    savevideo.py [url] [filename]
    """
    options = webdriver.ChromeOptions();
    for opt in CHROME_OPTIONS:
        options.add_argument(opt)

    vid_id = vidurl + printtimedelta(starttime) + printtimedelta(timespan) + str(len(text))
    vid_id = "".join([c for c in vid_id if c.isalpha() or c.isdigit() or c in '._-']).rstrip() + '.mp4'
    cached = os.path.join(CACHE, vid_id)

    if use_cache and os.path.exists(cached):
        shutil.copy(cached, outputfile)
        print "Got from cache: %s" % vidurl
        return

    try:
        browser = webdriver.Chrome(chrome_options=options)
        browser.get(vidurl)

        wait = ui.WebDriverWait(browser, 10)
        wait.until(lambda driver: driver.find_element_by_css_selector('.jwvideo'))

        vidbox = browser.find_element_by_css_selector('.jwplayer')
        vidbox.click()

        wait.until(lambda driver: driver.find_element_by_css_selector('.jwvideo video'))
        
        vid = browser.find_element_by_css_selector('.jwvideo video')
        vidsrc = vid.get_attribute("src")
        vidbox.click()

        if starttime is None:
            cmd = [VIDTOOL, '-y', '-i', vidsrc]
        else:
            ss = '-ss %s' % printtimedelta(starttime)
            t = '-t %s' % printtimedelta(timespan)
            cmd = [VIDTOOL, '-y', ss, '-i', vidsrc, t]

        if text is not None:
            drawtext="-vf drawtext=\"fontfile=Arvo-Bold.ttf:text='%s':fontsize=40:fontcolor=white:x=20:y=(main_h-text_h-20)\"" % text
            cmd.append(drawtext)

        # Set video bitrate to 901kB/s
        cmd.append('-b:v 901k')
        cmd.append(outputfile)

        cmd = ' '.join(cmd)
        print cmd
        os.system(cmd)

        if use_cache:
            if not os.path.exists(CACHE):
                os.makedirs(CACHE)
            shutil.copy(outputfile, cached)

    except TimeoutException:
        print "Timeout, No video found."
    
    browser.quit()

def main(fragmentsfile):
    fragmentsdict = json.load(fragmentsfile)
    fragments = fragmentsdict['fragments']
    name = os.path.basename(os.path.splitext(fragmentsfile.name)[0])

    folder = os.path.join('vids', name + datetime.now().strftime('%Y%m%d_%H%M'))
    if not os.path.exists(folder):
        os.makedirs(folder)

    for i,fragment in enumerate(fragments):
        prid = fragment['prid']
        url = fragmenturl(fragment)
        begin = parsetimedelta(fragment['start_time'])
        end = parsetimedelta(fragment['end_time'])
        text = subtitle(fragment['text'])
        t = end - begin
        filepath = os.path.join(folder,  '%03d-%s-%09d.mp4' % (i, prid, begin.seconds))
        download(url, filepath, begin, t, text)

    concat(folder)

def concat(folder):
    # Merge all videos using ffmpeg
    inputfiles = os.path.join(folder, '*.mp4')
    with open('_tmp_filelist.txt','w') as filelist:
        filelist.write('\n'.join([("file '%s'" % f) for f in glob(inputfiles)]) + '\n')

    # Concatenate the videos
    outputfile = os.path.join(folder, 'compilation.mp4')
    if USE_MENCODER:
        cmd = ['mencoder', '-oac mp3lame', '-ovc copy', inputfiles, '-o', 'outputfile']
    else:
        cmd = ['ffmpeg', '-f', 'concat', '-i', '_tmp_filelist.txt', '-c', 'copy', outputfile]
    os.system(' '.join(cmd))    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process fragments file and build video.')
    parser.add_argument('-d','--download', default=None, type=argparse.FileType('r'), help='File with list of clips in JSON to download and concat.')
    parser.add_argument('-c','--concat', default=None, type=str, help='Folder with clips to assemble (no download).')
    args = parser.parse_args()

    if args.download:
        main(args.download)
    elif args.concat:
        concat(args.concat)
    else:
        parser.print_help()
