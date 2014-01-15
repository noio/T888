T888
====

Use regex to select subtitles and build fragments from NPO video.

Usage
-----

Download program information and subtitles from omroep.nl:

	./getsubtitles.py

Search the subtitles:

	zoekT888.py [-h] [--program_regex PROGRAM_REGEX] [--subs SUBS]
	                   [--program_info PROGRAM_INFO] [--shuffle] [--offset OFFSET]
	                   [--start_padding START_PADDING] [--end_padding END_PADDING]
	                   [--match_only] [--verbose]
	                   search_regex output
	Query the T888 database to find fragments, and build a fragments file from it.
	positional arguments:
	  search_regex          search query
	  output                file to save fragments to

	optional arguments:
	  -h, --help            show this help message and exit
	  --program_regex PROGRAM_REGEX, -p PROGRAM_REGEX
	                        define in which tv program to search
	  --subs SUBS           folder where to search for subtitle files
	  --program_info PROGRAM_INFO
	                        folder where to search for program info
	  --shuffle             Shuffle the clips.
	  --offset OFFSET       insert an offset for each subtitle, >0 is later, <0
	                        earlier
	  --start_padding START_PADDING
	                        insert a padding to the start of the subtitle, >0 is
	                        later, <0 earlier
	  --end_padding END_PADDING
	                        insert a padding to the end of the subtitle, >0 is
	                        later, <0 earlier
	  --match_only, -m      Include only the matching part of the regex.
	  --verbose, -v         Print more info.

Build the movie:

	build.py [-h] [-d DOWNLOAD] [-c CONCAT]

	Process fragments file and build video.

	optional arguments:
	  -h, --help            show this help message and exit
	  -d DOWNLOAD, --download DOWNLOAD
	                        File with list of clips in JSON to download and
	                        concat.
	  -c CONCAT, --concat CONCAT
	                        Folder with clips to assemble (no download).

Dependencies
------------

Ubuntu:
* Selenium: `sudo pip install selenium`
* pyvirtualdisplay: `sudo pip install pyvirtualdisplay`

OSX:

* Selenium: `sudo pip install selenium`
* ffmpeg: `brew install ffmpeg --with-freetype`
