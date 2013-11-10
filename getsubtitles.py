#!/usr/bin/env python
""" Scraper for T888 subtitle data from the npo/uitzendingemist site
"""

# Dit is nog geen scraper ^^ ^^.
import os
os.system("mkdir kro-subtitles")
os.system("curl -0 http://www.hackdeoverheid.nl/wp-content/uploads/sites/10/2013/11/kro-subtitles.zip | tar -zx -C subtitles")
