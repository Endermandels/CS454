from collections import namedtuple
import math
import csv

class TF_IDF(object):
    """
    Calculates the Term Frequency - Inverted Document Frequency.
    """
    
    def __init__(self, dataFile):
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
                        term_to_docs[term] = 1
                        touched_terms.add(term)
                    elif not term in touched_terms:
                        term_to_docs[term] += 1
                        touched_terms.add(term)

                    if not term in term_counts:
                        term_counts[term] = 1
                    else:
                        term_counts[term] += 1
                doc_to_terms[row[0]] = DocTerms(len(terms), term_counts)

        return doc_to_terms, term_to_docs

    def tf_idf(self, Q, k):
        """
        Calculates the relevance of every document given the query

        Returns up to k of the most relevant documents in descending order of relevance
        """
        def sort_func(tup):
            return tup[1]

        result = []
        
        for d in self.doc_to_terms.keys():
            relevance = self.relevance(d, Q)
            if relevance > 0:
                result.append((d, relevance))

        result.sort(reverse=True, key=sort_func)
        return result[:k]

    def relevance(self, d, Q):
        """
        Returns the relevance of a document given the query
        """
        result = 0

        for term in Q.split():
            if term in self.doc_to_terms[d].counts:
                result += self.tf(d, term) / self.term_to_docs[term]

        return result

    def tf(self, d, t):
        """ Term Frequency """
        return math.log(1 + self.doc_to_terms[d].counts[t] / self.doc_to_terms[d].size)

def main():
    tf_idf = TF_IDF('wine.csv')
    for row in tf_idf.tf_idf('tremendous', 5):
        print(row)

if __name__ == '__main__':
    main()