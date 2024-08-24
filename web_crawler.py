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
METADATA_FN = 'metadata.dat'
ADJ_MATRIX_FN = 'adjacency_matrix.csv'
BACKUP_PERIOD = 100 # how many loops before backing up metadata 

def dprint(s):
	if DEBUG:
		print(s)

def store_data(data, fn):
	try:
		with open(fn, 'wb') as file:
			pickle.dump(data, file)
	except Exception as e:
		dprint(f'! Encountered error: {e}')

def load_data(fn, default=None):
	data = default
	try:
		with open(fn, 'rb') as file:
			data = pickle.load(file)
	except Exception as e:
		dprint(f'! Encountered error: {e}')
	return data

def save_data(stack, touched, adj_dict, metadata):
	dprint('Saving data...')
	store_data(stack, STACK_FN)
	store_data(touched, TOUCHED_FN)
	store_data(adj_dict, ADJ_DICT_FN)
	store_data(metadata, METADATA_FN)

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
		print(	f"! Permission denied: Unable to create folder"
				" '{fn}' in the current directory.")
	except OSError as e:
		print(f"! OS error occurred: {e}")
	except Exception as e:
		print(f"! Unexpected error: {e}")
	sys.exit(1)

def filter_links(href):
	"""
	Filter invalid or unhelpful links.
	"""
	if href:
		return not re.compile('/wiki/Special:Random').search(href)
	return False

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

def build_adj_matrix(adj_dict):
	"""Creates an adjacency matrix for a list of URLs."""
	urls = adj_dict.keys()
	n = len(urls)
	adjacency_matrix = np.zeros((n, n), dtype=int)

	# Populate the adjacency matrix
	for i, url in enumerate(urls):
		links = adj_dict[url]
		if len(links) > 0:
			for j, target_url in enumerate(urls):
				if target_url in links:
					adjacency_matrix[i][j] = 1

	df = pd.DataFrame(adjacency_matrix, columns=urls)
	df.to_csv(ADJ_MATRIX_FN, index=False)
	dprint('Created adjaceny matrix successfully')

def save_page(page, folder, url):
	sha256_hash = hashlib.sha256()
	sha256_hash.update((url.encode('utf-8')))
	fn = sha256_hash.hexdigest()
	# fn = re.sub(r'[^a-zA-Z0-9_\-.]', '_', url)
	cwd = os.getcwd()
	path = os.path.join(cwd, f'{folder}/{fn}.html')
	dprint(f'Saving HTML doc to path: {path}')
	if not os.path.exists(path):
		try:
			with open(path, 'w', encoding='UTF-8') as file:
				file.write(str(page.prettify()))
			dprint('Saved HTML page successfully')
			return 1
		except Exception as e:
			dprint(f'! Encountered error while saving HTML page: {e}')
	else:
		dprint(f'! Hash collision: skipping HTML doc')
	return 0

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
	stack = load_data(STACK_FN, default=[
			  'https://en.wiktionary.org/wiki/Wiktionary:Main_Page'
			, 'https://en.wikipedia.org/wiki/Main_Page'
		]
	)
	adj_dict = load_data(ADJ_DICT_FN, default=dict())
	touched = load_data(TOUCHED_FN, default=set())
	pages_visited, docs_saved = load_data(METADATA_FN, default=(0,0))


	domains = [
		  'wikipedia'
		, 'wiktionary'
	]
	current_domain = ['']

	rp = RobotFileParser()

	create_folder(DOCS_FN)

	try:
		while len(stack) > 0:
			try:
				# Take top item off of stack
				url = stack.pop()

				# Validate Port
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

				# Do not open restricted URLs
				if not can_fetch(rp, url, current_domain):
					dprint(f'Skipping disallowed URL: {url}')
					continue

				link = requests.get(url)
				# Current_url may be different from url
				#   in case the random page is accessed
				touched.add(url)

				# Check if response is HTML
				if not 'text/html' in link.headers.get('Content-Type'):
					dprint(f'Skipping non-HTML content: {url}')
					continue

				dprint(f'Visited URL: {url}')

				# SAVE THIS!!!
				page = BeautifulSoup(link.text, 'html.parser')
				docs_saved += save_page(page, DOCS_FN, url)
				
				# Add current url to the adjacency dict
				adj_dict[url] = []

				# Parse for new links (DFS)
				body = page.find(id='bodyContent')
				if body:
					for link in body.find_all('a', href=filter_links):
						# Make sure the domain remains the same
						full_url = urljoin(url, link['href'])
						link_domain = urlparse(full_url).netloc
						if full_url in touched:
							continue
						touched.add(full_url)

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

						# Update Adjacency Matrix
						adj_dict[url].append(full_url)

				# DEBUG Metadata
				pages_visited += 1
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
						(pages_visited, docs_saved))

				time.sleep(1)
			except Exception as e:
				print(f'! Encountered error: {e}')
				save_data(
					stack, 
					touched, 
					adj_dict, 
					(pages_visited, docs_saved))
				return adj_dict
	except KeyboardInterrupt:
		save_data(
			stack, 
			touched, 
			adj_dict, 
			(pages_visited, docs_saved))
		return adj_dict

if __name__ == '__main__':
	adj_dict = main()
	if not adj_dict is None:
		dprint('Building adjacency matrix...')
		build_adj_matrix(adj_dict)
	else:
		print('! Unable to build adjaceny matrix (adj_dict is None)')
	print('Exiting...')

