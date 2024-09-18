from assignment3 import Ranking

import sys

def main(judgement_file):
    ranking = Ranking(judgement_file)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: python3 main.py <judgement_file>')
        sys.exit(1)
    main(sys.argv[1])