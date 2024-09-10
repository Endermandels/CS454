from collections import namedtuple
import math
import csv

class BM_25(object):
    def __init__(self, dataFile):
        self.avg_doc_len = 0
        self.doc_to_terms, self.term_to_docs = self.load_data(dataFile)

    def load_data(self, dataFile):
        """
        doc_to_terms maps the doc id to the total number of terms and the count of each term
        term_to_docs maps each term to a list of docs containing that term
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
                terms = row[1].split()
                for term in terms:
                    if not term in term_to_docs:
                        term_to_docs[term] = [row[0]]
                        touched_terms.add(term)
                    elif not term in touched_terms:
                        term_to_docs[term].append(row[0])
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
    
    def bm_25(self, query, k):
        def sort_func(tup):
            return tup[1]

        touched_docs = set()
        result = []
        
        for term in query.split():
            if term in self.term_to_docs:
                for d in self.term_to_docs[term]:
                    if d in touched_docs:
                        continue
                    touched_docs.add(d)
                    relevance = self.relevance(d, query)
                    if relevance > 0:
                        result.append((d, relevance))

        result.sort(reverse=True, key=sort_func)
        return result[:k]
    
    def relevance(self, d, Q):
        result = 0

        for term in Q.split():
            if term in self.doc_to_terms[d].counts:
                result += self.idf(term) *  self.tf(d, term) * self.qtf()

        return result
    
    def idf(self, term):
        n = len(self.doc_to_terms.keys())
        dft = len(self.term_to_docs[term])
        return math.log((n - dft + 0.5) / (dft + 0.5))
    
    def tf(self, d, term):
        k1 = 1.2
        b = 0.75
        ft = self.doc_to_terms[d].counts[term] / self.doc_to_terms[d].size
        d = self.doc_to_terms[d].size
        return math.log(((k1 + 1)*ft) / (k1((1-b)+b*(d/self.avg_doc_len)+ft)))
    
    def qtf(self):
        pass
    
def main():
    bm25 = BM_25('test.csv')
    # bm25.bm_25('mac watson', 5)

if __name__ == '__main__':
    main()