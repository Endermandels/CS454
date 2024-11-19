from urllib.parse import urljoin
from collections import Counter
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
import pickle

import sys

def filter_links(href):
	"""
	Filter invalid or unhelpful links.
	"""
	if href:
		# Do not include Random, as it could cause problems while storing the urls
		if re.compile('/wiki/Special:Random').search(href):
			return False
		if re.compile('#').search(href):
			return False
		if re.compile('Category:').search(href):
			return False
		if re.compile(':Citation').search(href):
			return False
		return True
	return False

def build_adj_dict(url_map: dict[str, str], save_fn: str):
    adj_dict = {}
    for url, docFN in url_map.items():
        with open(docFN, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            
            links = {}
            for link in soup.find_all('a', href=filter_links):
                full_url = urljoin(url, link['href'])
                
                if full_url in links:
                    links[full_url] += 1
                else:
                    links[full_url] = 1
            
            adj_dict[url] = links
            
    with open(save_fn, 'wb') as file:
        pickle.dump(adj_dict, file)
    return adj_dict

def build_adj_matrix(adj_dict: dict[str, dict[str, int]], save_fn: str):
    """
    Creates an adjacency matrix for a list of URLs.
    """
    urls = adj_dict.keys()
    n = len(urls)
    adjacency_matrix = np.zeros((n, n), dtype=np.uint8)

    # Populate the adjacency matrix
    for i, url in enumerate(urls):
        links = adj_dict[url]
        for j, target_url in enumerate(urls):
            if target_url in links and i != j:
                adjacency_matrix[i][j] = links[target_url]

    df = pd.DataFrame(adjacency_matrix, index=urls, columns=urls)
    with open(save_fn, 'wb') as file:
        pickle.dump(df, file)
    return df
    
def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '-d':
            with open('_url_map.dat', 'rb') as file:
                print(build_adj_dict(pickle.load(file), '_adj_dict.dat'))
        elif sys.argv[1] == '-m':
            with open('_adj_dict.dat', 'rb') as file:
                print(build_adj_matrix(pickle.load(file), '_adj_matrix.dat'))
    else:
        print('usage: python3 build_adj_matrix.py [-m | -d]')
            

if __name__ == '__main__':
    main()