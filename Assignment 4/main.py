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

def create_index(fn, rebuild):
    schema = Schema(url=ID(stored=True, unique=True), title=TEXT(stored=True), content=TEXT(stored=True))
    
    if os.path.exists(fn):
        if rebuild:
            shutil.rmtree(fn)
        else:
            return index.open_dir(fn, schema=schema)

    os.makedirs(fn)
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
    title = str(page.title.string) if page.title else 'No Title'
    content = page.get_text(separator=' ', strip=True).lower()
    return title, content

def add_docs(ind, docs_fn, url_map):
    if not os.path.exists(docs_fn):
        print(f'! Error: No {docs_fn} folder')
        sys.exit(1)

    writer = ind.writer()

    for url, fn in url_map.items():
        if os.path.isfile(fn):
            with open(fn, 'r', encoding='utf-8') as file:
                title, content = extract_content(file.read())
                writer.add_document(url=url, title=title, content=content)
                print("added document")
    
    writer.commit()

def insert_ORs(string):
    words = string.split()
    new_string = ''
    cnt = 0
    for word in words:
        new_string += word
        if cnt < len(words)-1:
            new_string += ' OR '
        cnt += 1
    return new_string

def print_hits(results):
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

def query_session(ind):
    try:
        with ind.searcher() as searcher:
            qp = QueryParser("content", ind.schema)
            limit = 10
            disjunctive = False
            while True:
                # Specify Limit using 'LIM' (case sensitive)
                user_query = input('> ').strip()
                if len(user_query) > 3 and user_query[0:3] == 'LIM':
                    try:
                        limit = int(user_query[3:])
                    except Exception as e:
                        print(f"Encountere error: {e}")
                    continue
                # Specify Conjunctive or Disjunctive
                if user_query == 'DIS' or user_query == 'OR':
                    disjunctive = True
                    continue
                if user_query == 'CON' or user_query == 'AND':
                    disjunctive = False
                    continue

                user_query = user_query.lower()
                
                # Insert OR's into disjunctive queries
                if disjunctive:
                    user_query = insert_ORs(user_query)

                query = qp.parse(user_query)
                results = searcher.search(query, terms=True, limit=limit)
                
                print_hits(results)
                
    except KeyboardInterrupt:
        print('Exiting...')

def main():
    rebuild = False
    if len(sys.argv) > 1 and sys.argv[1] == '-r':
        rebuild = True

    ind = create_index(IND_PATH, rebuild)
    url_map = unpickle_url_map(URL_MAP_PATH)
    if rebuild:
        add_docs(ind, DOCS_PATH, url_map)
    query_session(ind)

if __name__ == '__main__':
    main()
