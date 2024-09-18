from assignment3 import Ranking
import sys

def main(judgement_file, query_results):
    ranking = Ranking(judgement_file)
    lines = []
    
    with open(query_results, 'r') as file:
        lines = file.read().replace('\t', ' ').split('\n')

    try:
        while True:
            test_input = input('Enter <method> <line_number> <threshold>\n').split(' ')
            
            if len(test_input) != 3:
                print('Incorrect number of arguments\n')
                continue
            
            method = test_input[0]
            line_num = int(test_input[1]) - 1
            threshold = int(test_input[2])
            
            if not (0 <= line_num < len(lines)):
                print('Line number does not exist\n')
                continue
            if not (0 <= threshold <= 4):
                print('Threshold does not exist\n')
                continue
            
            satisfaction = -1
            
            if method == 'prec':
                satisfaction = ranking.prec(lines[line_num], threshold)
            elif method == 'recall':
                satisfaction = ranking.recall(lines[line_num], threshold)
            elif method == 'rr':
                satisfaction = ranking.rr(lines[line_num], threshold)
            elif method == 'f1':
                satisfaction = ranking.f1_score(lines[line_num], threshold)
            elif method == 'ndcg':
                satisfaction = ranking.ndcg(lines[line_num])
            else:
                print('Method does not exist\n')
                continue
                
            print('Satisfaction score:', satisfaction, '\n')
                
    except KeyboardInterrupt:
        print('\nExiting...')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: python3 main.py <judgement_file> <queries_results>')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])