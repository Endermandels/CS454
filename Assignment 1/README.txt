# Web Crawler

## Running

To run this program:

	python3 web_crawler.py

To delete all .dat files and the docs folder:

	python3 clear_save_data.py

## Customization

There are a number of constants at the beginning of the web_crawler.py file to customize the program's execution.  Here is a list of the constants and how they are used:

- DEBUG 		Boolean: Whether to print out the debug statements
- USER_AGENT	String:  What user agent the crawler uses (defaults to '*')
- DOCS_FN 		String:  Folder name containing all HTML documents
- URL_MAP_FN	String:  URL map file name
- METADATA_FN	String:  Metadata file name
- ADJ_MATRIX_FN	String:  Adjacency matrix file name
- BACKUP_PERIOD	Int:     How many pages saved before backing up metadata
- DOCS_COUNT 	Int:     How many documents need to be collected (-1 means until stack is empty)
- DOMAINS		List:    Domains containing these strings will be promoted
- SEED_URLS		List:    Seeded URLs used in the first execution of the program