#!/usr/bin/env python

import argparse
import sys
import datetime
import json
from datetime import timedelta
import os
import time
import subprocess
from selenium import webdriver

### FUNCTIONS ###

def prid2url(pr_id):

	with open('kro-subtitles/program_info/' + pr_id + '.json', 'r') as IN:
	    broken_json = IN.readline()

	pr_info = json.loads(broken_json[14:-3])

	pr_date = pr_info['gidsdatum']
	pr_date2 = "{}-{}-{}".format(pr_date[8:10], pr_date[5:7], pr_date[:4])

	pr_titel = pr_info['streamSense']['program'].replace('_','-')

	return "http://www.npo.nl/{}/{}/{}".format(pr_titel, pr_date2, pr_id)

def parsetimedelta(timestring):
	d = timedelta(hours=int(timestring[0:2]), minutes=int(timestring[3:5]), 
		seconds=int(timestring[6:8]), milliseconds=int(timestring[9:12]))
	return d

def printtimedelta(td):
	return '%02d:%02d:%02d.%03d' % (td.seconds//3600, (td.seconds//60) % 60, td.seconds % 60, td.microseconds/1000)

def subtitle(inp):
	inp = inp.replace(':','')
	for i in range(0, len(inp), 25):
		inp = inp[:i] + '\n' + inp[i:]
	
	return inp

def download(vidurl, outputfile, starttime=None, timespan=None, text=None):
	""" Saves a video for a given npo.nl url, using ffmpeg
	savevideo.py [url] [filename]
	"""
	USER_AGENT_STRING = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.30.1 (KHTML, like Gecko) Version/6.0.5 Safari/536.30.1"
	# USER_AGENT_STRING_IPAD = "Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3"
	# url = 'http://www.npo.nl/heibel-langs-de-lijn/10-03-2013/KRO_1408553'
	# url2 = 'http://www.npo.nl/brieven-boven-water/07-09-2013/KRO_1642075'

	OPTS = ["--user-agent="+USER_AGENT_STRING, "--disable-extensions", "--disable-bundled-ppapi-flash", "--disable-internal-flash"] 
        # Sicco specific:
	#OPTS = ["--user-data-dir=/home/sicco/.config/chromium/Default" ,"--user-agent="+USER_AGENT_STRING, "--disable-extensions", "--disable-bundled-ppapi-flash", "--disable-internal-flash"] 
	options = webdriver.ChromeOptions();

	for opt in OPTS:
		options.add_argument(opt)

	# capabilities = webdriver.DesiredCapabilities.CHROME
	# capabilities["chrome.switches"] = OPTS

	browser = webdriver.Chrome(chrome_options=options)

	browser.get(vidurl)

	time.sleep(4)

	try:
		vidbox = browser.find_element_by_css_selector('.jwplayer')
		vidbox.click()

		# vid.click()
		time.sleep(2)
		vidbox.click()

		vid = browser.find_element_by_css_selector('.jwvideo video')

		vidsrc = vid.get_attribute("src")

		if starttime is None:
			cmd = ['ffmpeg', '-y', '-i', vidsrc]
			#cmd = ['avconv', '-y', '-i', vidsrc]
		else:
			ss = '-ss %s' % printtimedelta(starttime)
			t = '-t %s' % printtimedelta(timespan)
			cmd = ['ffmpeg', '-y', ss, '-i', vidsrc, t]
                        # Sicco specific:
			#cmd = ['avconv', '-y', ss, '-i', vidsrc, t]

		if text is not None:
			drawtext="-vf drawtext=\"fontfile=Arvo-Bold.ttf:text='%s':fontsize=40:fontcolor=white:x=20:y=(main_h-text_h-20)\"" % text
			cmd.append(drawtext)

                # Set video bitrate to 901kB/s
                cmd.append('-b:v 901k')
		cmd.append(outputfile)

		cmd = ' '.join(cmd)
		print cmd
		os.system(cmd)

		# subprocess.call(cmd)
		# open('npo.html', 'w').write(browser.page_source.encode('utf-8'))
		# elem = browser.find_element_by_name('p')

		# response = urllib2.urlopen('http://python.org/')
	except:
		pass
	browser.quit()

def main(fragmentsfile):
	fragments = [eval(line) for line in fragmentsfile]

        if not os.path.exists('vids'):
            os.makedirs('vids')

        timestamp = str(datetime.datetime.now()).replace(' ', '_')[:-7]
        if not os.path.exists('vids/' + timestamp):
            os.makedirs('vids/' + timestamp)

	for i,fragment in enumerate(fragments):
		prid = fragment[0]
		url = prid2url(prid)
		begin = parsetimedelta(fragment[1])
		end = parsetimedelta(fragment[2])
		text = subtitle(fragment[3])
		t = end - begin
		download(url, 'vids/' + timestamp + '/%03d-%s-%09d.mp4' % (i, prid, begin.seconds), begin, t, text)
		# print begin, t
		# print printtimedelta(begin), printtimedelta(t)

        # Merge all videos together
        os.system('mencoder -oac mp3lame -ovc copy vids/' + timestamp + '/*.mp4 -o vids/' + timestamp + '/compilation.mp4')

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process fragments file and build video.')
	parser.add_argument('fragments', type=argparse.FileType('r'), help='File with list of desired fragments in JSON.')
	args = parser.parse_args()

	main(args.fragments)
