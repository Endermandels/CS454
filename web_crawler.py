"""
Assignment 1 - Web Crawler
Elijah Delavar
CS 454-01
x/xx/2024
"""

import requests						# requests webpages
from bs4 import BeautifulSoup		# converts html to english
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
from copy import deepcopy
import time 
import re

DEBUG = True
USER_AGENT = '*'

def dprint(s):
	if DEBUG:
		print(s)


def filter_links(href):
	"""
	Filter invalid or unhelpful links
	"""
	return href

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
	qq = [
		'https://en.wikipedia.org/wiki/Main_Page', 
	]
	robots_urls = [
		'https://en.wikipedia.org/robots.txt'
	]
	domains = [
		urlparse(qq[0]).netloc
	]

	# Metadata
	touched = set()
	pages_visited = 0
	current_domain = 0
	count = 0 # For setting a specified limit

	rp = RobotFileParser()
	rp.set_url(robots_urls[0])
	rp.read()

	while len(qq) > 0:
		try:
			url = qq.pop(0)

			# Do not open restricted URLs
			if not rp.can_fetch(USER_AGENT, url):
				dprint(f'Skipping URL: {url}')
				continue

			link = requests.get(url)
			# Current_url may be different from url
			#   in case the random page is accessed
			current_url = link.url 
			touched.add(current_url)

			# Check if response is HTML
			if not 'text/html' in link.headers.get('Content-Type'):
				dprint(f'Skipping non-HTML content: {current_url}')
				continue

			# SAVE THIS!!!
			page = BeautifulSoup(link.text, 'html.parser')
			
			# Parse for new links (BFS)
			body = page.find(id='bodyContent')
			for link in body.find_all('a', href=filter_links):
				full_url = urljoin(current_url, link['href'])
				link_domain = urlparse(full_url).netloc
				if (full_url in touched or 
					link_domain != domains[current_domain]):
					continue
				else:
					qq.append(full_url)
					touched.add(full_url)

			# DEBUG Metadata
			pages_visited += 1
			dprint(f'Length of Queue: {len(qq)}')
			dprint(f'Pages visited: {pages_visited}')

			time.sleep(1)
		except Exception as e:
			print(f'Encountered error: {e}')
			print('Exiting...')

if __name__ == '__main__':
	main()
