import numpy as np
import pandas as pd
from collections import defaultdict


def __pagerank(M, d: float = 0.85):
    """
    PageRank algorithm with explicit number of iterations. Returns ranking of nodes (pages) in the adjacency matrix.

    Parameters
    ----------
    M : numpy array
        adjacency matrix (square) where M_i,j represents the link from 'j' to 'i', such that for all 'j'
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


def __build_transition_matrix(links):
    """
    Build the adjacency matrix used in the PageRank algorithm

    Parameters:
        links: the links dataframe based on the links.tsv file.

    Returns:
        square matrix where M_i,j represents the link from 'j' to 'i', such that for all 'j'
        sum(i, M_i,j) = 1
    """

    # Create list of all unique articles mentioned as starting points or endpoints of links.
    nodes = np.unique(links[['linkSource', 'linkTarget']].values.flatten())
    N = len(nodes)
    node_indices = {node: idx for idx, node in enumerate(nodes)}

    M = np.zeros((N, N))
    from_idx = links['linkSource'].map(node_indices).values
    to_idx = links['linkTarget'].map(node_indices).values
    np.add.at(M, (to_idx, from_idx), 1) #We put a 1 when there is a link

    # Normalize columns to sum to 1 and handle dangling nodes (no outgoing edge)
    column_sums = M.sum(axis=0)
    dangling_nodes = (column_sums == 0)
    M[:, dangling_nodes] = 1.0 / N
    column_sums = M.sum(axis=0)
    M = M / column_sums

    return M, nodes


def compute_distances(links, probs_posterior, paths_homing_in, proportion: float = 0.2):
    """
    Compute the path-independent distances for all pairs of articles for which it is possible, as per the
    equations (3) and (4) of the Wikispeedia paper.
    """

    M, nodes =  __build_transition_matrix(links)
    ranks = __pagerank(M)

    # Properties that were tested and validated: every rank is inferior to 1, the sum of all ranks is 1
    pagerank_scores = dict(zip(nodes, ranks))

    # Initialize the distances matrix
    nodes = np.unique(links[['linkSource', 'linkTarget']].values.flatten())
    distances_counts = defaultdict(int) # used in computing the average of path distances
    distances = defaultdict(int) # Interface: distances[article1][article2] = d(article1, article2)

    def compute_path_distance(i, path):
        goal = path[-1]
        sum_p = 0
        for j in range(i, len(path) - 1):
            if probs_posterior[goal][path[j]][path[j+1]] == 0:
                print(f'{goal=}, {path[j]=}, {path[j+1]=}')
                continue
            sum_p -= np.log(probs_posterior[goal][path[j]][path[j+1]])
        return sum_p / -np.log(pagerank_scores[goal])

    # Fill in distances without normalization and distances_count for one path
    def distances_along_path(path):
        goal = path[-1]
        for i in range(0, len(path) - 1): # len(path) - 1: We don't consider the distance from the goal to itself
            if path[i] not in links['linkSource'].values or goal not in links['linkSource'].values:
                continue
            distances[(goal, path[i])] += compute_path_distance(i, path)
            distances_counts[(goal, path[i])] += 1
        return path

    # Compute the distances and distances_counts matrix by passing through all the paths and incrementing the two matrices accordingly
    stop = int(len(paths_homing_in) * proportion)
    for path in paths_homing_in[:stop]:
        distances_along_path(path)

    # Normalize the distances according to the number of occurrences of given distance in the paths
    for key in distances:
        distances[key] /= distances_counts[key]

    # Put every undefined distance to a negative value.
    distances.default_factory = lambda: -1

    return distances