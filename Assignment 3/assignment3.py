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
            rel - number of relevant urls based on judgement score
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
        """
        Returns recall
        
        Formula: rel / total
        Terms:
            rel     - number of relevant urls based on judgement score
            total   - total number of relevant urls
        """
        parts = query_line.split()
        rel = 0
        
        for url in parts[3:self.NUM_RETURNED+3]:
            score = self.url_scores[parts[0]].get(url, -1)
            if score >= thresh:
                rel += 1
        
        total = 0
        
        for score in self.url_scores[parts[0]].values():
            if score >= thresh:
                total += 1
        
        return rel / total if total != 0 else 0

    def rr(self, query_line, thresh):
        parts = query_line.split()
        pos = 0
        
        for i, url in enumerate(parts[3:self.NUM_RETURNED+3]):
            score = self.url_scores[parts[0]].get(url, -1)
            if score >= thresh:
                pos = 1 / (i-3)
        
        return pos

    def f1_score(self, query_line, thresh):
        a = 0.5

        recall = self.recall(query_line, thresh)
        prec = self.prec(query_line, thresh)

        return 1 / (a * (1 / prec) + (1 - a) * (1 / recall)) if recall != 0 and prec != 0 else 0
        
    def ndcg(self, query_line):
        return -1