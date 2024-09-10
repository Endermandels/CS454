from collections import namedtuple
import math
import csv

class TF_IDF(object):
	def __init__(self, dataFile):
		# Docs: key = doc id, value = doc contents
		self.docs = self.load_data(dataFile)

	def load_data(self, dataFile):
		"""
		Each document id is the key in docs
		The value in docs is a tuple containing the total number of terms and
			the count of each term in the document
		"""
		docs = dict()

		with open(dataFile, mode='r') as file:
			csvFile = csv.reader(file)
			DocStats = namedtuple('DocStats', ['size', 'counts'])
			for row in csvFile:
				term_counts = dict()
				terms = row[1].split()
				for term in terms:
					if not term in term_counts:
						term_counts[term] = 1
					else:
						term_counts[term] += 1
				docs[row[0]] = DocStats(len(terms), term_counts)

		return docs

	def tf_idf(self, Q, k):
		pass

	def relevance(self, d, Q):
		pass

	def tf(self, d, t):
		return math.log(1 + self.docs[d].counts[t] / self.docs[d].size)

def main():
	tf_idf = TF_IDF('wine.csv')
	print(tf_idf.tf('4999', 'fruit'))

if __name__ == '__main__':
	main()