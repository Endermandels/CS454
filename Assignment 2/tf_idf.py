from collections import namedtuple
import math
import csv

class TF_IDF(object):
	def __init__(self, dataFile):
		# Docs: key = doc id, value = doc contents
		self.doc_to_terms, self.term_to_docs = self.load_data(dataFile)
		print(self.doc_to_terms)
		print()
		print(self.term_to_docs)

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
				doc_to_terms[row[0]] = DocTerms(len(terms), term_counts)

		return doc_to_terms, term_to_docs

	def tf_idf(self, Q, k):
		def sort_func(tup):
			return tup[1]

		touched_docs = set()
		result = []
		
		for term in Q.split():
			if term in self.term_to_docs:
				for d in self.term_to_docs[term]:
					if d in touched_docs:
						continue
					touched_docs.add(d)
					relevance = self.relevance(d, Q)
					if relevance > 0:
						result.append((d, relevance))

		result.sort(reverse=True, key=sort_func)
		return result[:k]

	def relevance(self, d, Q):
		result = 0

		for term in Q.split():
			if term in self.doc_to_terms[d].counts:
				result += self.tf(d, term) / len(self.term_to_docs[term])

		return result

	def tf(self, d, t):
		return math.log10(1 + self.doc_to_terms[d].counts[t] / self.doc_to_terms[d].size)

def main():
	tf_idf = TF_IDF('test.csv')
	print(tf_idf.tf_idf('hello w', 2))

if __name__ == '__main__':
	main()