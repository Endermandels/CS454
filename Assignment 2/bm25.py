from collections import namedtuple
import math
import csv

DEBUG = False

class BM_25(object):
    def __init__(self, dataFile):
        self.avg_doc_len = 0
        self.doc_to_terms, self.term_to_docs = self.load_data(dataFile)

    def load_data(self, dataFile):
        """
        doc_to_terms maps the doc id to the total number of terms and the count of each term
        term_to_docs maps each term to a list of docs containing that term
        update the avg_doc_len with the average document length
        """
        doc_to_terms = dict()
        term_to_docs = dict()
        
        with open(dataFile, mode='r') as file:
            csvFile = csv.reader(file)
            DocTerms = namedtuple('DocTerms', ['size', 'counts'])
            for row in csvFile:
                if row[0] == 'id':
                    continue
                touched_terms = set()
                term_counts = dict()
                terms = row[1].strip().split()
                for term in terms:
                    if not term in term_to_docs:
                        term_to_docs[term] = 1
                        touched_terms.add(term)
                    elif not term in touched_terms:
                        term_to_docs[term] += 1
                        touched_terms.add(term)

                    if not term in term_counts:
                        term_counts[term] = 1
                    else:
                        term_counts[term] += 1
                size = len(terms)
                self.avg_doc_len += size
                doc_to_terms[row[0]] = DocTerms(size, term_counts)

        self.avg_doc_len = self.avg_doc_len / len(doc_to_terms.keys())

        return doc_to_terms, term_to_docs
    
    def bm25(self, query, k):
        def sort_func(tup):
            return tup[1]

        result = []
        
        for d in self.doc_to_terms.keys():
            relevance = self.relevance(d, query)
            if relevance > 0:
                result.append((d, relevance))

        result.sort(reverse=True, key=sort_func)
        return result[:k]
    
    def relevance(self, d, query):
        result = 0

        split_query = query.strip().split()
        for term in split_query:
            if term in self.doc_to_terms[d].counts:
                idf = self.idf(term)
                tf = self.tf(d, term)
                qtf = self.qtf(split_query, term)
                result += idf *  tf * qtf
                if DEBUG:
                    print(idf)
                    print(tf)
                    print(qtf)
                    print()

        return result
    
    def idf(self, term):
        n = len(self.doc_to_terms.keys())
        dft = self.term_to_docs[term]
        if DEBUG:
            print('n: ', n)
            print('dft: ', dft)
        return math.log((n - dft + 0.5) / (dft + 0.5))
    
    def tf(self, doc, term):
        k1 = 1.2
        b = 0.75
        ft = self.doc_to_terms[doc].counts[term] / self.doc_to_terms[doc].size
        d = self.doc_to_terms[doc].size
        if DEBUG:
            print('ft: ', ft)
            print('d: ', d)
            print('avg len d: ', self.avg_doc_len)
        return ((k1 + 1)*ft) / (k1*((1-b)+b*(d/self.avg_doc_len))+ft)
    
    def qtf(self, split_query, term):
        k2 = 500
        qft = len([i for i in split_query if i == term]) / len(split_query)
        if DEBUG:
            print('qft: ', qft)
        return ((k2 + 1)*qft) / (k2 + qft)
    
def main():
    bm25 = BM_25('wine.csv')
    for row in bm25.bm25('mac watson', 5):
        print(row)

if __name__ == '__main__':
    main()