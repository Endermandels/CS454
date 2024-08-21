"""
Assignment 1 - Web Crawler
Elijah Delavar
CS 454-01
x/xx/2024
"""

import requests						# requests webpages
from bs4 import BeautifulSoup		# converts html to english
from urllib.robotparser import RobotFileParser
									# parses robots.txt
import re							# regular expressions
import time
from copy import deepcopy

DEBUG = True
SEED_URLS = [
	('https://en.wikipedia.org/wiki/Main_Page', 
		'https://en.wikipedia.org/robots.txt')
] # (url, robots.txt)

def dprint(s):
	if DEBUG:
		print(s)

def main():
	"""
	STEPS:

	1. Seed queue with initial URLs
	2. While queue is not empty:
		i. 		Pop URL, L, from queue
		ii. 	If L is not HTML or in visited dictionary, skip it
		iii.	Download HTML page for L
		iv.		Parse HTML page for new links
		v.		Append new links to end of queue

	NOTES:

	Add time delay to be polite
	Filter out disallowed URLs
	"""

	# Queue
	qq = deepcopy(SEED_URLS)

	# rp = RobotFileParser()
	# rp.set_url()

if __name__ == '__main__':
	main()
