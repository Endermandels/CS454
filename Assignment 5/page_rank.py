import numpy as np
import pandas as pd
import pickle

def init_transition_matrix(adj_matrix: pd.DataFrame):
    c = 0.9
    sums = adj_matrix.sum(axis=1).to_numpy()
    link_matrix = adj_matrix.mul(c/sums, axis=0)
    
    n = adj_matrix.shape[0]
    leap_matrix = np.full((n, n), (1-c)/n)
    return leap_matrix + link_matrix.to_numpy()

def page_rank(adj_matrix: pd.DataFrame, iterations: int, save_fn: str):
    """
    Take in adjacency matrix
    Calculate rank over given iterations
    Return dataframe with adjusted scores
    """
    n = adj_matrix.shape[0]
    scores_vector = np.full(n, 1/n)
    transition_matrix = init_transition_matrix(adj_matrix)
    for _ in range(iterations):
        scores_vector = scores_vector @ transition_matrix
    rankings = pd.DataFrame(scores_vector, index=adj_matrix.index)
    with open(save_fn, 'wb') as file:
        pickle.dump(rankings, file)
    return rankings

def main():
    with open('_adj_matrix.dat', 'rb') as file:
        print(page_rank(pickle.load(file), 20, '_rankings.dat'))
    
if __name__ == '__main__':
    main()