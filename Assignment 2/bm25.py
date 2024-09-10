class BM_25(object):
    def __init__(self, dataFile):
        pass

    def bm_25(self, query, k):
        pass
    
def main():
    bm25 = BM_25('wine.csv')
    bm25.bm_25('mac watson', 5)

if __name__ == '__main__':
    main()