"""
Assignment 1 - Web Crawler
Elijah Delavar
CS 454-01
9/4/2024
"""

import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
from datetime import datetime
import pandas as pd
import numpy as np
import hashlib
import pickle
import time
import sys 
import re
import os

DEBUG = True
USER_AGENT = '*'
DOCS_FN = 'docs' # folder name containing all HTML documents
STACK_FN = 'stack.dat'
TOUCHED_FN = 'touched.dat'
ADJ_DICT_FN = 'adj_dict.dat'
COLLISIONS_FN = 'collisions.dat'
METADATA_FN = 'metadata.dat'
ADJ_MATRIX_FN = 'adjacency_matrix.csv'
BACKUP_PERIOD = 100 # how many loops before backing up metadata
DOCS_COUNT = 6000 # how many documents need to be collected (-1 for until stopped)

def dprint(s):
	if DEBUG:
		print(s)

def store_data(data, fn):
	"""
	Stores data in a pickle file of filename fn in the cwd
	"""
	try:
		with open(fn, 'wb') as file:
			pickle.dump(data, file)
	except Exception as e:
		dprint(f'! Encountered error: {e}')

def load_data(fn, default=None):
	"""
	Loads data from a pickle file of filename fn in the cwd

	Defaults to default if no file is detected (or any other error)
	"""
	data = default
	try:
		with open(fn, 'rb') as file:
			data = pickle.load(file)
	except Exception as e:
		dprint(f'! Encountered error: {e}')
	return data

def save_data(stack, touched, adj_dict, collisions, metadata):
	dprint('Saving data...')
	store_data(stack, STACK_FN)
	store_data(touched, TOUCHED_FN)
	store_data(adj_dict, ADJ_DICT_FN)
	store_data(collisions, COLLISIONS_FN)
	store_data(metadata, METADATA_FN)

def create_folder(fn):
	dprint(f"Creating folder '{fn}'")
	try:
		cwd = os.getcwd()
		path = os.path.join(cwd, fn)

		if not os.path.exists(path):
			os.makedirs(path)
			dprint(f"Folder '{fn}' created successfully at {path}.")
		else:
			dprint(f"Folder '{fn}' already exists at {path}.")
		return
	except Exception as e:
		print(f"! Encountered error: {e}")
	sys.exit(1)

def filter_links(href):
	"""
	Filter invalid or unhelpful links.
	"""
	if href:
		# Do not include Random, as it could cause problems while storing the urls
		return not re.compile('/wiki/Special:Random').search(href)
	return False

def new_domain(rp, url, prev_domain, delay):
	"""
	Updates RobotParser instance with new robots.txt url.
	Changes the program delay according to robots.txt info.
	"""
	domain = urlparse(url).netloc
	if domain != prev_domain[0]:
		# Get new robots.txt url
		dprint(f'Switching from domain {prev_domain[0]} to {domain}')
		rp.set_url(f'https://{domain}/robots.txt')
		rp.read()
		prev_domain[0] = domain

		# Determine delay
		crawl_delay = rp.crawl_delay(USER_AGENT)
		if not crawl_delay:
			crawl_delay = 1
		request_rate = rp.request_rate(USER_AGENT)
		interval = 0
		if request_rate:
			interval = request_rate.seconds / request_rate.requests
		new_delay = max(crawl_delay, interval)
		if new_delay != delay[0]:
			delay[0] = new_delay
			dprint(f'Delay updated to: {new_delay}')

def build_adj_matrix(adj_dict):
	"""
	Creates an adjacency matrix for a list of URLs.
	"""
	urls = adj_dict.keys()
	n = len(urls)
	adjacency_matrix = np.zeros((n, n), dtype=int)

	# Populate the adjacency matrix
	for i, url in enumerate(urls):
		links = adj_dict[url]
		# Assume pages link to themselves (refresh button)
		adjacency_matrix[i][i] = 1 
		if len(links) > 0:
			for j, target_url in enumerate(urls):
				if target_url in links:
					adjacency_matrix[i][j] = 1

	df = pd.DataFrame(adjacency_matrix, columns=urls)
	df.to_csv(ADJ_MATRIX_FN, index=False)
	dprint('Created adjaceny matrix successfully')

def save_page(page, folder, url, collisions):
	"""
	Save HTML document to local folder
	Name HTML document by hashing the url using sha256.
	Collisions produce the same path name, but increase a counter suffix.
	If a collision occurs, add the colliding url to the collision path.
	When loading up a url doc, 
	  first check if the hashed path exists in collisions.dat.
		If it does, check if the url is in the collisions.
			If it is, take the path with the index of the url + 1.
			Otherwise, take the original path.
	"""
	sha256_hash = hashlib.sha256()
	sha256_hash.update((url.encode('utf-8')))
	fn = sha256_hash.hexdigest()
	cwd = os.getcwd()
	path = os.path.join(cwd, f'{folder}/{fn}.html')
	dprint(f'Saving HTML doc to path: {path}')

	if os.path.exists(path):
		# Hash collision
		dprint(f'Hash collision: {path}')
		if not path in collisions:
			collisions[path] = [url]
		else:
			collisions[path].append(url)
		path = os.path.join(cwd, f'{folder}/{fn}_{len(collisions[path])}.html')
		dprint(f'Creating new path: {path}')

	# Write HTML document to disk
	try:
		with open(path, 'w', encoding='UTF-8') as file:
			file.write(str(page.prettify()))
		dprint('Saved HTML page successfully')
		return 1
	except Exception as e:
		dprint(f'! Encountered error while saving HTML page: {e}')
	return 0

def main():
	"""
	Crawls the web, specifically focusing on 
		the domains listed in the domains list.

	Returns the adjacency matrix of the collected urls.
	"""

	# Metadata
	stack = load_data(STACK_FN, default=[
			  'https://en.wiktionary.org/wiki/Wiktionary:Main_Page'
			, 'https://en.wikipedia.org/wiki/Main_Page'
		]
	)
	adj_dict = load_data(ADJ_DICT_FN, default=dict())
	touched = load_data(TOUCHED_FN, default=set())
	collisions = load_data(COLLISIONS_FN, default=dict())
	pages_visited, docs_saved = load_data(
		  METADATA_FN
		, default=(0,0)
	)

	# If enough documents have already been collected
	if DOCS_COUNT > 0 and docs_saved >= DOCS_COUNT:
		print('! No more documents are required: '
			f'docs_saved={docs_saved} DOCS_COUNT={DOCS_COUNT}')
		return None # Do not need to create the adjacency matrix again

	# Domains containing the following strings will be promoted
	domains = [
		  'wikipedia'
		, 'wiktionary'
	]

	# Keeps track of the current domain in case the domain changes
	#   and the RobotParser needs to be updated
	current_domain = ['']

	rp = RobotFileParser()
	delay = [1] # Sleep delay in seconds

	create_folder(DOCS_FN)

	try:
		while len(stack) > 0:
			try:
				# Pop top item of stack
				url = stack.pop()

				# Validate Port (this resolves a niche error)
				parsed_url = urlparse(url)
				try:
					port = parsed_url.port
				except Exception as e:
					dprint(f'! Encountered error '
							'while checking port validity: {e}')
					continue
				if port is not None and (port < 0 or port > 65535):
					dprint(f'Skipping invalid port URL: {url}')
					continue

				# Check if the domain changes and update RobotParser
				new_domain(rp, url, current_domain, delay)

				# Do not open restricted URLs
				if not rp.can_fetch(USER_AGENT, url):
					dprint(f'Skipping disallowed URL: {url}')
					continue

				link = requests.get(url)
				touched.add(url)

				# Check if response is HTML
				if not 'text/html' in link.headers.get('Content-Type'):
					dprint(f'Skipping non-HTML content: {url}')
					continue

				dprint(f'Visited URL: {url}')
				pages_visited += 1

				# Collect and save HTML document
				page = BeautifulSoup(link.text, 'html.parser')
				saved = save_page(page, DOCS_FN, url, collisions)
				if saved == 0:
					dprint('Skipping url with bad HTML document')
					continue
				docs_saved += saved
				
				# Add current url to the adjacency dict
				adj_dict[url] = []

				# Parse for new links (DFS)
				body = page.find(id='bodyContent')
				if body:
					for link in body.find_all('a', href=filter_links):
						full_url = urljoin(url, link['href'])

						# Skip already seen urls
						if full_url in touched:
							continue
						touched.add(full_url)

						# Promote domains with strings listed in domains list
						link_domain = urlparse(full_url).netloc
						contains_domain = False
						for domain in domains:
							if re.compile(domain).search(link_domain):
								contains_domain = True
								break
						# If it contains a desired domain, push to top of stack
						if contains_domain:
							stack.append(full_url)
						# Otherwise, insert at bottom of stack
						else:
							stack.insert(0, full_url)

						# Update adjacency dictionary
						adj_dict[url].append(full_url)

				# DEBUG Metadata
				dprint(f'Length of Stack: {len(stack)}')
				dprint(f'Pages visited: {pages_visited}')
				dprint(f'Docs saved: {docs_saved}')
				dprint('')

				# Backup Metadata
				if pages_visited % BACKUP_PERIOD == 1:
					save_data(
						stack, 
						touched, 
						adj_dict, 
						collisions,
						(pages_visited, docs_saved)
					)

				# Check if enough documents have been collected
				if DOCS_COUNT > 0 and docs_saved >= DOCS_COUNT:
					dprint(f'Collected required {DOCS_COUNT} documents')
					save_data(
						stack, 
						touched, 
						adj_dict, 
						collisions,
						(pages_visited, docs_saved)
					)
					return adj_dict

				time.sleep(delay[0])
			except Exception as e:
				print(f'! Encountered error: {e}')
				save_data(
					stack, 
					touched, 
					adj_dict, 
					collisions,
					(pages_visited, docs_saved)
				)
				return adj_dict
	except KeyboardInterrupt:
		save_data(
			stack, 
			touched, 
			adj_dict, 
			collisions,
			(pages_visited, docs_saved)
		)
		return adj_dict

if __name__ == '__main__':
	start_time = datetime.now()
	adj_dict = main()
	if not adj_dict is None:
		dprint('Building adjacency matrix...')
		build_adj_matrix(adj_dict)
	else:
		print('! Unable to build adjaceny matrix (adj_dict is None)')
	finish_time = datetime.now() - start_time
	print(f'Total runtime: {finish_time}')
	print('Exiting...')
