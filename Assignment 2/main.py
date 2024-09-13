from tf_idf import TF_IDF
from bm25 import BM_25
import sys

def main(filename):
    
    tf_idf = TF_IDF(filename)
    bm25 = BM_25(filename)

    try:
        while True:
            algo = input("Algorithm ('t' for tf_idf; 'b' for bm25): ")
            if not algo in ['t', 'b']:
                print("Unclear algorithm (please specify using 't' or 'b')")
                continue
            query = input("Query: ")
            num_results = int(input("Number of returned results: "))
            
            if algo.lower() == 't':
                result = tf_idf.tf_idf(query, num_results)
            else:
                result = bm25.bm25(query, num_results)
            
            print('\n###### RESULTS ######\n')

            for row in result:
                print(row)
            
            print()

    except KeyboardInterrupt:
        print('\nStopping program')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: python3 main.py <filename>')
        sys.exit(1)
    main(sys.argv[1])