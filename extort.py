#!/usr/bin/env python
# encoding: utf-8
"""
extort.py

Created by Giorgio Stampa on 2009-03-13.
Copyright (c) 2009 . All rights reserved.
"""

import sys
import os

def all_files(root, patterns='*', single_level=False, yield_folders=False):
	import fnmatch
	# Expand patterns from semicolon-separated string to list
	patterns = patterns.split(';')
	for path, subdirs, files in os.walk(root):
		if yield_folders:
			files.extend(subdirs)
		files.sort()
		for name in files:
			for pattern in patterns:
				if fnmatch.fnmatch(name, pattern):
					yield os.path.join(path, name)
					break
		if single_level:
			break

def spot_instrumental(lyrics):
	firstline=lyrics.splitlines()[0].lower()
	if firstline.find("instrumental")==-1:
		return False
	else:
		return True

def main():
	import mutagen
	
	songs=list(all_files("./iTunes Media/Music", "*.mp3;*.MP3;*.m4a;*.M4A"))
	# print songs
	for songpath in songs:
		# print songpath
		artist=""
		title=""
		album=""
		lyrics=None

		victim=mutagen.File(songpath)
		if type(victim)==type(None):
			continue
		
		if "USLT::'eng'" in victim.keys():
			if 'TPE1' in victim.keys():
				artist=unicode(victim['TPE1']).lower().replace(os.sep, '_')
			if 'TIT2' in victim.keys():
				title=unicode(victim['TIT2']).lower().replace(os.sep, '_')
			if 'TALB' in victim.keys():
				album=unicode(victim['TALB']).lower().replace(os.sep, '_')
			lyrics=unicode(victim["USLT::'eng'"]).lower().replace('\x0d\x0a', '\x0a').replace('\x0d', '\x0a')
		elif '\xa9lyr' in victim.keys():
			if '\xa9ART' in victim.keys():
				artist=unicode(victim['\xa9ART'][0]).lower().replace(os.sep, '_')
			if '\xa9nam' in victim.keys():
				title=unicode(victim['\xa9nam'][0]).lower().replace(os.sep, '_')
			if '\xa9alb' in victim.keys():
				album=unicode(victim['\xa9alb'][0]).lower().replace(os.sep, '_')
			lyrics=unicode(victim['\xa9lyr'][0]).lower().replace('\x0d\x0a', '\x0a').replace('\x0d', '\x0a')
		else:
			if victim.keys()==[]:	# debug
				print
				print songpath
				print
			continue
		
		if spot_instrumental(lyrics):
			continue

		if artist.startswith("the "):
			artist=artist.partition("the ")[2]

		where="./Extorted Lyrics"
		if album=="":
			textpath=where+"/"+artist+" "+title+".txt"
		else:
			textpath=where+"/"+artist+" "+title+" ("+album+").txt"

		print textpath.encode("utf-8")
		text=file(textpath, "wb")
		# text.write("\xef\xbb\xbf")	# UTF-8 BOM
		text.write("\xef\xbb\xbf"+lyrics.encode("utf-8"))
		text.close


if __name__ == '__main__':
	main()

