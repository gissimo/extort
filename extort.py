#!/usr/bin/env python
# encoding: utf-8

"""
extort.py

Created by Giorgio Stampa on 2009-03-13.
Copyright (c) 2009-2014 . All rights reserved.
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


def normalize(field):
	return unicode(field).lower().replace(os.sep, '_')


def clean_text(lyrics):
	return unicode(lyrics).lower().replace('\x0d\x0a', '\x0a').replace('\x0d', '\x0a').replace('\x0b', '\x0a').replace('\x0c', '\x0a').replace(u'\x85', '\x0a').replace(u'\u2028', '\x0a').replace(u'\u2029', '\x0a')+'\x0a'


def main():
	import mutagen
	import hashlib
	import imghdr
	import mutagen.id3
	mutagen.id3.APIC.HashKey = property(lambda s: '%s:%s' % (s.FrameID, len(s.data)))

	songs=list(all_files("./iTunes Media/Music/", "*.mp3;*mP3;*Mp3;*.MP3;*.m4a;*m4A;*M4a;*.M4A"))
	# print songs
	for songpath in songs:
		# print songpath
		artist=""
		title=""
		album=""
		lyrics=None
		instrum=True
		covers=[]
		hashes=[]
		pixtypes=[]
		string=""

		victim=mutagen.File(songpath)
		if type(victim)==type(None):
			continue

		if victim.mime[0]=="audio/mp3":
			if 'TPE1' in victim.keys():
				artist=normalize(victim['TPE1'])
				if artist.startswith("the "):
					artist=artist.partition("the ")[2]
				string+="/ "+artist+" "
			if 'TALB' in victim.keys():
				album=normalize(victim['TALB'])
				string+="/ "+album+" "
			if 'TIT2' in victim.keys():
				title=normalize(victim['TIT2'])
				string+="/ "+title+" "
			if "USLT::'eng'" in victim.keys():
				lyrics=clean_text(victim["USLT::'eng'"])
				instrum=spot_instrumental(lyrics)
				if instrum:
					string+="/ instrumental "
				else:
					string+="/ lyrics "
			for tag in victim.keys():
				if tag.startswith("APIC"):
					covers.append(victim[tag].data)
					hashes.append(hashlib.md5(victim[tag].data).hexdigest()[0:3])
					mime=imghdr.what(None,victim[tag].data)
					if mime==None:
						mime='jpeg'
					pixtypes.append(mime)
					string+="/ "+mime+" "

		if victim.mime[0]=="audio/mp4":
			if '\xa9ART' in victim.keys():
				artist=normalize(victim['\xa9ART'][0])
				if artist.startswith("the "):
					artist=artist.partition("the ")[2]
				string+="/ "+artist+" "
			if '\xa9alb' in victim.keys():
				album=normalize(victim['\xa9alb'][0])
				string+="/ "+album+" "
			if '\xa9nam' in victim.keys():
				title=normalize(victim['\xa9nam'][0])
				string+="/ "+title+" "
			if '\xa9lyr' in victim.keys():
				lyrics=clean_text(victim['\xa9lyr'][0])
				instrum=spot_instrumental(lyrics)
				if instrum:
					string+="/ instrumental "
				else:
					string+="/ lyrics "
			if "covr" in victim.keys():
				for i in range(len(victim['covr'])):
					covers.append(victim['covr'][i])
					hashes.append(hashlib.md5(victim['covr'][i]).hexdigest()[0:3])
					mime=imghdr.what(None,victim['covr'][i])
					if mime==None:
						mime='jpeg'
					pixtypes.append(mime)
					string+="/ "+mime+" "

		# write lyrics file
		if instrum==False:
			where="./Extorted Lyrics"
			if album=="":
				textpath=where+"/"+artist+" "+title+".txt"
			else:
				textpath=where+"/"+artist+" "+title+" ("+album+").txt"

			text=file(textpath, "wb")
			# text.write("\xef\xbb\xbf")	# UTF-8 BOM
			text.write("\xef\xbb\xbf"+lyrics.encode("utf-8"))
			text.close()

		# write cover art file
		if len(covers)>0:
			for i in range(len(covers)):
				covrpath="./Covers/"+album+" ("+hashes[i]+")."+pixtypes[i]
				pix=file(covrpath, "wb")
				pix.write(covers[i])
				pix.close()

		print string


if __name__ == '__main__':
	main()

