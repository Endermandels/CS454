from assignment3 import Ranking
import sys

def main(judgement_file, query_results):
    ranking = Ranking(judgement_file)
    
    with open(query_results, 'r') as file:
        first_line = file.readline()
        prec = ranking.prec(first_line.strip(), 0)
        print(prec)
        
        # for line in file:
        #     prec = ranking.prec(line.strip(), 0)
        #     print(prec)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: python3 main.py <judgement_file> <queries_results>')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])