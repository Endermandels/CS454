from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from bs4 import BeautifulSoup
from whoosh import index
import os.path
import shutil
import pickle
import sys

IND_PATH = '_index'
DOCS_PATH = 'docs'
URL_MAP_PATH = '_url_map.dat'

def create_index(fn):
    if os.path.exists(fn):
        shutil.rmtree(fn)

    os.makedirs(fn)
    schema = Schema(url=ID(stored=True, unique=True), title=TEXT(stored=True), content=TEXT(stored=True))
    return index.create_in(fn, schema)

def unpickle_url_map(fn):
    """
    @return url_map (key = url, val = doc path)
    """

    try:
        with open(fn, 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        print(f'! Error while parsing {fn}: {e}')
        sys.exit(1)

def extract_content(html):
    page = BeautifulSoup(html, 'html.parser')
    title = page.title.string if page.title else 'No Title'
    content = page.get_text().lower()
    return title, content

def add_docs(ind, docs_fn, url_map):
    if not os.path.exists(docs_fn):
        print(f'! Error: No {docs_fn} folder')
        sys.exit(1)

    writer = ind.writer()
    cnt = 1
    batch_size = 2

    for url, fn in url_map.items():
        if os.path.isfile(fn):
            with open(fn, 'r', encoding='utf-8') as file:
                title, content = extract_content(file.read())
                writer.add_document(url=url, title=title, content=content)
                if cnt % batch_size == 0:
                    writer.commit()
                    writer = ind.writer()
    
    writer.commit()

def query_session(ind):
    try:
        with ind.searcher() as searcher:
            while True:
                user_query = input('> ').strip().lower()

                query = QueryParser("content", ind.schema).parse(user_query)
                results = searcher.search(query, terms=True)
                
                for r in results:
                    print(r, r.score)
                    if results.has_matched_terms():
                        print(results.matched_terms())
    except KeyboardInterrupt:
        print('Exiting...')

def main():
    ind = create_index(IND_PATH)
    url_map = unpickle_url_map(URL_MAP_PATH)
    add_docs(ind, DOCS_PATH, url_map)
    query_session(ind)

if __name__ == '__main__':
    main()
