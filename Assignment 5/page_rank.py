import numpy as np
import pandas as pd
import pickle

def init_transition_matrix(adj_matrix: pd.DataFrame) -> np.ndarray:
    """
    Creates the transition matrix used in the PageRank iterations.
    The random surfer constant (c) is set to 0.9.
    
    Params
        adj_matrix: DataFrame containing adjacency matrix of url links
        
    Returns
        Transition matrix
    """
    c = 0.9
    sums = adj_matrix.sum(axis=1).to_numpy()
    link_matrix = adj_matrix.mul(c/sums, axis=0)
    
    n = adj_matrix.shape[0]
    leap_matrix = np.full((n, n), (1-c)/n)
    return leap_matrix + link_matrix.to_numpy()

def page_rank(adj_matrix: pd.DataFrame, iterations: int, save_fn: str) -> pd.DataFrame:
    """
    Calculate PageRank of adjacency matrix over specified iterations.
    Save results to save_fn.
    
    Params
        adj_matrix: DataFrame containing adjacency matrix of url links
        iterations: Number of iterations to calculate PageRank
        save_fn:    File name to save rankings to
    
    Returns
        Rankings DataFrame
    """
    n = adj_matrix.shape[0]
    scores_vector = np.full(n, 1/n)
    transition_matrix = init_transition_matrix(adj_matrix)
  
    for _ in range(iterations):
        scores_vector = scores_vector @ transition_matrix
        
    rankings = pd.DataFrame(scores_vector, index=adj_matrix.index, columns=['Rank'])
    with open(save_fn, 'wb') as file:
        pickle.dump(rankings, file)
        
    return rankings

def main():
    """
    Calculates the PageRank given an adjacency matrix.
    """
    with open('_adj_matrix.dat', 'rb') as file:
        print(page_rank(pickle.load(file), 20, '_rankings.dat'))
    
if __name__ == '__main__':
    main()