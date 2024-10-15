from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh import index
import os.path
import shutil

IND_PATH = '_index'

def create_index(fn):
    if (os.path.exists(fn)):
        shutil.rmtree(fn)


    os.makedirs(fn)
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True))
    return index.create_in(fn, schema)

def add_docs(ind):
    writer = ind.writer()
    writer.add_document(title=u'doc', content=u'py doc hello big world oh', path=u'/a')
    writer.add_document(title=u'doc2', content=u'my oh my', path=u'/b')
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
    add_docs(ind)
    query_session(ind)

if __name__ == '__main__':
    main()
