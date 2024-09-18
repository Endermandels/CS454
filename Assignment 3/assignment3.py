from collections import defaultdict
import math

class Ranking(object):
    """
    Rank query satisfaction
    """
    
    def __init__(self, judgement_file):
        """
        url_scores = {
            query: {
                url: score
            }
        }
        """
        
        self.NUM_RETURNED = 10
        self.url_scores = defaultdict(dict)
        with open(judgement_file, 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                self.url_scores[parts[0]][parts[1]] = int(parts[2])
                
    def prec(self, query_line, thresh):
        """
        Returns precision
        
        Formula: rel / k
        terms:
            rel - relevance of a url based on judgement score
            k   - number of returned results
        """
        parts = query_line.split()
        rel = 0
        
        for url in parts[3:self.NUM_RETURNED+3]:
            score = self.url_scores[parts[0]].get(url, -1)
            if score >= thresh:
                rel += 1
        
        return rel / self.NUM_RETURNED

    def recall(self, query_line, thresh):
        return -1

    def rr(self, query_line, thresh):
        return -1

    def f1_score(self, query_line, thresh):
        return -1

    def ndcg(self, query_line):
        return -1