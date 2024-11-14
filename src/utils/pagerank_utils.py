import numpy as np
import pandas as pd

def pagerank(M, d: float = 0.85):
    """
    PageRank algorithm with explicit number of iterations. Returns ranking of nodes (pages) in the adjacency matrix.

    Parameters
    ----------
    M : numpy array
        adjacency matrix where M_i,j represents the link from 'j' to 'i', such that for all 'j'
        sum(i, M_i,j) = 1
    d : float, optional
        damping factor, by default 0.85

    Returns
    -------
    numpy array
        a vector of ranks such that v_i is the i-th rank from [0, 1],

        
    Modified version of the implementation found on the Wikipedia PageRank page: https://en.wikipedia.org/wiki/PageRank, usable under the Creative Commons Attribution-ShareAlike 4.0 License
    """
    N = M.shape[1]
    w = np.ones(N) / N
    M_hat = d * M
    teleport = (1 - d) / N
    v = M_hat @ w + teleport
    while(np.linalg.norm(w - v) >= 1e-10):
        w = v
        v = M_hat @ w + teleport
    return v



def build_transition_matrix(links):
    '''
    links: the links pd dataframe based on the links tsv file.
    '''

    #Create list of all unique articles mentioned as starting points or endpoints of links.
    nodes = np.unique(links[['linkSource', 'linkTarget']].values.flatten())
    N = len(nodes)
    node_indices = {node: idx for idx, node in enumerate(nodes)}


    M = np.zeros((N, N))
    from_idx = links['linkSource'].map(node_indices).values
    to_idx = links['linkTarget'].map(node_indices).values
    np.add.at(M, (to_idx, from_idx), 1) #We put a 1 when there is a link


    #Normalize columns to sum to 1 and handle dangling nodes (no outgoing edge)
    column_sums = M.sum(axis=0)
    dangling_nodes = (column_sums == 0)
    M[:, dangling_nodes] = 1.0 / N
    column_sums = M.sum(axis=0)
    M = M / column_sums

    return M, nodes