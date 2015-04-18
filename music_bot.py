#!/bin/python
# -*- coding: utf-8 -*-

from pdb import set_trace
import praw
import youtube_dl
import os
import sys
import json
import zlib

class MusicBot(object):

	def __init__(self, PATH):
		self.PATH = PATH
		self.DATABASE = os.environ['MUSIC_BOT'] + '/urls.json'
		self.GIGABYTE = 1000000000
		self.SUPPORTED = [
			'youtube',
			'soundcloud',
			'mixcloud',
		]


	#def push_2_host(self):

	def read_urls(self):
		with open(self.DATABASE, 'a+') as fd:
			try:
				return json.loads(zlib.decompress(fd.read()))
			except zlib.error:
				return []

	def write_urls(self, urls):
		with open(self.DATABASE, 'w+') as fd:
			fd.write(zlib.compress(json.dumps(urls)))

	def youtube(self, urls):
		ydl_opts = {
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '192',
			}],
			'outtmpl': self.PATH + '%(title)s.%(ext)s',
			'max_filesize': self.GIGABYTE,
			'updatetime': False,
			'prefer_ffmpeg': True,
			'ignoreerrors': True,
		}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download(urls)

	def run(self):
		urls = self.read_urls()
		jobs = []

		submissions = praw.Reddit(user_agent='Awesome Music').get_subreddit(sys.argv[1]).get_hot(limit=100)
		for x in submissions:
			if not x.url in urls and any(u in x.url for u in self.SUPPORTED):
				jobs.append(x.url)

		if jobs:
			self.youtube(jobs)
			self.write_urls(jobs)
		os.system('rm ' + self.PATH + '*.m4a')

if __name__ == '__main__':
	_subreddits = [
		'trance',
		'atmosphericdnb',
		'dnb',
		'edm',
		'electrohouse',
		'swinghouse',
		'tranceandbass',
	]

	if 'MUSIC_BOT' not in os.environ:
		print 'Missing MUSIC_BOT path in environ'
		sys.exit(1)

	if sys.argv[1] not in _subreddits:
		print 'Missing subreddit %s, register it first' % sys.argv[1]
		sys.exit(1)

	path = os.environ['MUSIC_BOT'] + sys.argv[1] + '/'
	if not os.path.exists(path):
		os.makedirs(path)
	
	b = MusicBot(path)	
	b.run()
