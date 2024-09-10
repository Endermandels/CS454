import math
import csv

class TF_IDF(object):
	def __init__(self, dataFile):
		# Docs: key = doc id, value = doc contents
		self.docs = self.load_data(dataFile)
		print(self.docs)

	def load_data(self, dataFile):
		docs = dict()

		with open(dataFile, mode='r') as file:
			csvFile = csv.reader(file)
			for row in csvFile:
				docs[row[0]] = row[1]

		return docs

	def tf_idf(self, Q, k):
		pass

	def relevance(self, d, Q):
		pass

	def tf(self, d, t):
		pass
		# return math.log(1 + )

def main():
	tf_idf = TF_IDF('wine.csv')

if __name__ == '__main__':
	main()