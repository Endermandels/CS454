from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from bs4 import BeautifulSoup
from whoosh import index
import whoosh
import os.path
import shutil
import pickle
import sys

import time
import string

import whoosh.searching

DEBUG = True

IND_PATH = '_index' # Whoosh-generated index directory
URL_MAP_PATH = '_url_map.dat' # Pickled dictionary (key: url, val: document name in docs folder)
DOCS_PATH = 'docs' # Raw HTML of collected web pages
# NOTE: DOCS_PATH has to be named 'docs' because of how the _url_map.dat 
# dictionary stores the paths to files

def create_index(fn : str, rebuild : bool) -> index.Index:
    """
    Create Index Schema with following attributes (all stored in the index):
        url: ID, unique
        title: TEXT
        content: TEXT
    
    Params
        fn:      Folder name to store/load index
        rebuild: Whether to rebuild the index or load from existing index directory

    Returns
        Whoosh Index, whether the index was rebuilt
    """
    schema = Schema(
        url=ID(stored=True)
        , title=TEXT(stored=True)
        , content=TEXT(stored=True)
    )
    
    if os.path.exists(fn):
        if rebuild:
            shutil.rmtree(fn)
        else:
            return index.open_dir(fn, schema=schema), False

    os.makedirs(fn)
    return index.create_in(fn, schema), True

def unpickle_url_map(fn : str) -> dict:
    """
    Load the url_map dicionary from the pickled file with specified file name.
    url_map structure: (key: url, val: document name in docs folder)

    Params
        fn: File name of pickled url_map dictionary

    Returns
        url_map
    """
    try:
        with open(fn, 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        print(f'! Error while parsing {fn}: {e}')
        sys.exit(1)

def extract_content(html : str) -> tuple[str, str]:
    """
    Extract the title and text content of a given string of HTML code

    Params
        html: String of HTML code
    
    Returns
        (title of HTML page, content of HTML page)
    """
    page = BeautifulSoup(html, 'html.parser')
    title = str(page.title.string) if page.title else 'No Title'
    content = page.get_text(separator=' ', strip=True).lower()
    # translate code from this stack overflow: 
    # https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string
    content = content.translate(str.maketrans('','', string.punctuation))
    return title, content

def add_docs(ind : index.Index, docs_fn : str, url_map : dict):
    """
    Add documents in docs folder to index with url from url_map
    and title/content from the extracted HTML page.
    This can take multiple minutes to complete.

    Params
        ind:     Whoosh Index
        docs_fn: File name of docs folder
        url_map: Dictionary of url keys and doc_fn values
    """
    if not os.path.exists(docs_fn):
        print(f'! Error: No {docs_fn} folder')
        sys.exit(1)

    writer = ind.writer(limitmb=512, procs=4, multisegment=True)

    print('Creating index...')

    for url, fn in url_map.items():
        if os.path.isfile(fn):
            with open(fn, 'r', encoding='utf-8') as file:
                title, content = extract_content(file.read())
                writer.add_document(url=url, title=title, content=content)
                if DEBUG:
                    print('document added')
    
    writer.commit()

def insert_ORs(query : str) -> str:
    """
    Insert 'OR' strings inbetween the words of given query
    so that whoosh's search will be disjunctive instead of conjunctive

    Params
        query: User query string

    Returns
        Disjunctive query string
    """
    words = query.split()
    new_string = ''
    cnt = 0
    for word in words:
        new_string += word
        if cnt < len(words)-1:
            new_string += ' OR '
        cnt += 1
    return new_string

def print_hits(results : whoosh.searching.Results):
    """
    Print out the results of the user query.

    Params
        results: Results of the user query
    """
    for i, hit in enumerate(results):
        print(f'------------------------------------ RESULT {i+1} ------------------------------------')
        print('Title:', hit['title'])
        print('URL:\n  ', hit['url'])
        print()
        print('Score:\n  ', hit.score)
        print()
        if results.has_matched_terms():
            print('Matched Terms:\n  ', hit.matched_terms())
            print()
        print('Highlights:\n')
        print(hit.highlights("content"))
        print()

def query_session(ind : index.Index):
    """
    Create a terminal session where the user can query the indexed documents.
    Valid Terminal Commands (case sensitive):
        LIM <amount>    (limits the amount of returned results; no less than 1; default is 10)
        DIS             (switches the queries to disjunctive queries; also works with 'OR')
        CON             (switches the queries to conjunctive queries; also works with 'AND')
        <query>         (any other input; will return results from)
    
    To exit from the terminal session, send the interrupt signal (Ctrl + C for Windows/Linux; Cmd + . for Mac)

    Params
        ind: Whoosh index
    """
    try:
        with ind.searcher() as searcher:
            print(f'Document count: {searcher.doc_count()}')
            qp = QueryParser("content", ind.schema)
            limit = 10
            disjunctive = False
            while True:
                # Specify Limit using 'LIM' (case sensitive)
                user_query = input('> ').strip()
                if len(user_query) > 3 and user_query[0:3] == 'LIM':
                    try:
                        limit = max(int(user_query[3:]), 1)
                        print('Returned results limit:', limit)
                    except Exception as e:
                        print(f"! Error: {e}")
                    continue
                # Specify Conjunctive or Disjunctive (case sensitive)
                if user_query == 'DIS' or user_query == 'OR':
                    disjunctive = True
                    print('Queries are now disjunctive')
                    continue
                if user_query == 'CON' or user_query == 'AND':
                    print('Queries are now conjunctive')
                    disjunctive = False
                    continue

                user_query = user_query.lower()
                
                # Insert OR's into disjunctive queries
                if disjunctive:
                    user_query = insert_ORs(user_query)

                # Query index
                query = qp.parse(user_query)
                results = searcher.search(query, terms=True, limit=limit)
                
                # This helps with getting highlights, no matter the size of the document
                results.fragmenter.charlimit = None 
                
                # Print results
                print_hits(results)
                
    except KeyboardInterrupt:
        print('Exiting...')

def main():
    """
    Create an index over a directory of crawled HTML pages,
    then start an interactive query session in the terminal.

    Options
        -r : rebuild the index if it already exists
    """
    rebuild = False
    if len(sys.argv) > 1 and sys.argv[1] == '-r':
        rebuild = True

    ind, rebuilt = create_index(IND_PATH, rebuild)
    url_map = unpickle_url_map(URL_MAP_PATH)
    if rebuilt:
        start = time.time()
        add_docs(ind, DOCS_PATH, url_map)
        if DEBUG:
            print('Took:', time.time() - start, 'seconds')
    query_session(ind)

if __name__ == '__main__':
    main()
