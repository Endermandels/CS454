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
import pickle
import time
import sys 
import re
import os

DEBUG = True
USER_AGENT = '*'
DOCS_FN = 'docs' # folder name containing all HTML documents
BACKUP_PERIOD = 100 # how many loops before backing up metadata 

def dprint(s):
	if DEBUG:
		print(s)

def store_data(data, fn):
	try:
		with open(fn, 'wb') as file:
			pickle.dump(data, file)
	except Exception as e:
		dprint(f'Encountered error: {e}')

def load_data(fn, default=None):
	data = default
	try:
		with open(fn, 'rb') as file:
			data = pickle.load(file)
	except Exception as e:
		dprint(f'Encountered error: {e}')
	return data

def save_data(stack, touched, metadata):
	dprint('Saving data...')
	store_data(stack, 'stack.dat')
	store_data(touched, 'touched.dat')
	store_data(metadata, 'metadata.dat')

def create_folder(fn):
	try:
		cwd = os.getcwd()
		path = os.path.join(cwd, fn)

		# Check if the folder already exists
		if not os.path.exists(path):
			# Create the folder
			os.makedirs(path)
			dprint(f"Folder '{fn}' created successfully at {path}.")
		else:
			dprint(f"Folder '{fn}' already exists at {path}.")
		return
	
	except PermissionError:
		print(f"Permission denied: Unable to create folder '{fn}' in the current directory.")
	except OSError as e:
		print(f"OS error occurred: {e}")
	except Exception as e:
		print(f"Unexpected error: {e}")
	sys.exit(1)

def filter_links(href):
	"""
	Filter invalid or unhelpful links.
	"""
	return href

def can_fetch(rp, url, prev_domain):
	"""
	Updates RobotParser instance with new robots.txt url.
	Returns whether the url param can be fetched.
	"""
	domain = urlparse(url).netloc
	if domain != prev_domain[0]:
		dprint(f'Switching from domain {prev_domain[0]} to {domain}')
		rp.set_url(f'https://{domain}/robots.txt')
		rp.read()
		prev_domain[0] = domain
	return rp.can_fetch(USER_AGENT, url)

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

	# Metadata
	stack = [
			'https://en.wiktionary.org/wiki/Wiktionary:Main_Page',
			'https://en.wikipedia.org/wiki/Main_Page'
		]
	stack = load_data('stack.dat', default=stack)
	adj_matrix = {
		
	}
	touched = load_data('touched.dat', default=set())


	domains = [
		'wikipedia',
		'wiktionary',
	]

	pages_visited = load_data('metadata.dat', default=0)


	rp = RobotFileParser()
	current_domain = ['']

	create_folder(DOCS_FN)

	try:
		while len(stack) > 0:
			try:
				# Take top item off of stack
				url = stack.pop()


				# Do not open restricted URLs
				if not can_fetch(rp, url, current_domain):
					dprint(f'Skipping disallowed URL: {url}')
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

				dprint(f'Visited URL: {current_url}')

				# SAVE THIS!!!
				page = BeautifulSoup(link.text, 'html.parser')
				
				# Parse for new links (DFS)
				body = page.find(id='bodyContent')
				for link in body.find_all('a', href=filter_links):
					# Make sure the domain remains the same
					full_url = urljoin(current_url, link['href'])
					link_domain = urlparse(full_url).netloc
					if full_url in touched:
						continue

					# Does the link domain contain one of the desired domains?
					contains_domain = False
					for domain in domains:
						if re.compile(domain).search(link_domain):
							contains_domain = True
							break
					# If it contains a domain, push to top of stack
					if contains_domain:
						stack.append(full_url)
					# Otherwise, insert at bottom of stack
					else:
						stack.insert(0, full_url)
					touched.add(full_url)

				# DEBUG Metadata
				pages_visited += 1
				dprint(f'Length of Stack: {len(stack)}')
				dprint(f'Pages visited: {pages_visited}')
				dprint('')

				# Backup Metadata
				if pages_visited % BACKUP_PERIOD == 1:
					save_data(stack, touched, pages_visited)

				time.sleep(1)
			except Exception as e:
				print(f'Encountered error: {e}')
				save_data(stack, touched, pages_visited)
				print('Exiting...')
				return
	except KeyboardInterrupt:
		save_data(stack, touched, pages_visited)
		print('Exiting...')
		return

if __name__ == '__main__':
	main()
