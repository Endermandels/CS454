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
        
        self.NUM_RETURNED = 3
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
            score = self.url_scores[parts[0]].get(url, 0)
            if score >= thresh:
                rel += 1
        
        return rel / self.NUM_RETURNED

    def recall(self, query_line, thresh):
        """
        Returns recall (or 0 if the total number of relevant urls is 0)
        
        Formula: rel / total
        Terms:
            rel     - number of relevant urls based on judgement score
            total   - total number of relevant urls
        """
        parts = query_line.split()
        rel = 0
        
        for url in parts[3:self.NUM_RETURNED+3]:
            score = self.url_scores[parts[0]].get(url, 0)
            if score >= thresh:
                rel += 1
        
        total = 0
        
        for score in self.url_scores[parts[0]].values():
            if score >= thresh:
                total += 1
        
        return rel / total if total != 0 else 0

    def rr(self, query_line, thresh):
        """
        Returns reciprocal rank (or 0 if none of the returned urls are relevant)
        
        Formula: 1 / pos_r
        Terms:
            pos_r   - position of the first relevant url
        """
        parts = query_line.split()
        pos = 0
        
        for i, url in enumerate(parts[3:self.NUM_RETURNED+3]):
            score = self.url_scores[parts[0]].get(url, 0)
            if score >= thresh:
                pos = 1 / (i+1)
                break
        
        return pos

    def f1_score(self, query_line, thresh):
        """
        Returns F1 score (or 0 if recall and precision are 0)
        
        Formula: 1 / (a * (1 / prec) + (1 - a) * (1 / recall))
        Terms:
            a       - a constant which balances the weight of precision and recall
            prec    - precision
            recall  - recall
        """
        a = 0.5

        recall = self.recall(query_line, thresh)
        prec = self.prec(query_line, thresh)

        return 1 / (a * (1 / prec) + (1 - a) * (1 / recall)) if recall != 0 and prec != 0 else 0
        
    def ndcg(self, query_line):
        """
        Returns Normalized Discounted Cumulative Gain

        Formula (NDCG): dcg / idcg
        Formula (DCG): Sum from i = 1 to k (rel_i / log2 (i + 1))
        Formula (IDCG): DCG with optimal relevance order
        Terms:
            rel_i   - relevance judgement score of i-th url
            k       - number of returned results
        """

        parts = query_line.split()

        # DCG
        dcg = 0
        score_counts = [0,0,0,0,0] # counts of scores 0-4

        for i, url in enumerate(parts[3:self.NUM_RETURNED+3]):
            # i starts at 0, hence "i + 2" in the log
            dcg += self.url_scores[parts[0]].get(url, 0) / math.log2(i + 2) 
            print('dcg step', i, dcg)

        # IDCG
        idcg = 0

        for score in self.url_scores[parts[0]].values():
            score_counts[score] += 1

        idx = 4 # maximum score
        for i in range(self.NUM_RETURNED):
            while idx > 0:
                if score_counts[idx] > 0:
                    # print('results:', idx, i + 1)
                    idcg += idx / math.log2(i + 2)
                    score_counts[idx] -= 1
                    break
                else:
                    idx -= 1

        print('dcg', dcg, 'idcg', idcg)
        return dcg / idcg if idcg != 0 else 0