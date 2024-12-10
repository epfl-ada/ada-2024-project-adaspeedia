from collections import defaultdict
import numpy as np


def __count_occurrences(paths_no_backtrack):
    # N(A=a, G=g): the number of times 'a' was encountered on paths for which 'g' was the goal
    count_goal_article = defaultdict(lambda: defaultdict(int))
    # N(A’=a’, A=a, G=g): the number of times a’ was clicked in this situation
    count_goal_article_article_clicked = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    # Count the occurrences of a, a’ and g along every path
    for path in paths_no_backtrack:
        goal = path[-1]
        # Iterate through the path by getting each time one article and the one that was clicked from it.
        # It starts at (start_article, first_article_clicked) and ends with (before_last_article, goal).
        for article, article_clicked in zip(path, path[1:]):
            count_goal_article[goal][article] += 1
            count_goal_article_article_clicked[goal][article][article_clicked] += 1

    return count_goal_article, count_goal_article_article_clicked

def posterior_probabilites(paths_no_backtrack, out_links, out_degree):
    count_goal_article, count_goal_article_article_clicked = __count_occurrences(paths_no_backtrack)
    probs_posterior = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    # alpha_ is the Dirichlet parameter representing the initial confidence in the uniform prior distribution
    alpha_ = 0.1

    for g, article_counts in count_goal_article.items():
        for a, count in article_counts.items():
            for a_ in out_links[a]:
                # Use the formula (1) from the Wikispeedia paper
                probs_posterior[g][a][a_] = (
                        (count_goal_article_article_clicked[g][a][a_] + alpha_)
                        /
                        (count_goal_article[g][a] + alpha_ * out_degree[a])
                )

    return probs_posterior


def entropies_prior_posterior(paths_no_backtrack, probs_prior, probs_posterior, out_degree):
    def prior_entropies_along_path(path):
        """
        Turn a path into the prior entropy at each article along the path

        Parameters:
            path (array of strings): list of the titles of the articles along the path

        Returns:
            entropies (array of floats): list of the prior entropy values for each article along this path
        """
        # Skip the goal because the entropy is 0 at the goal
        return [-1 * out_degree[a] * probs_prior[a] * np.log(probs_prior[a]) for a in path[:-1]]

    def posterior_entropies_along_path(path):
        """
        Turn a path into the posterior entropy at each article along the path

        Parameters:
            path (array of strings): list of the titles of the articles along the path

        Returns:
            entropies (array of floats): list of the posterior entropy values for each article along this path
        """
        g = path[-1]
        # Skip the goal because the entropy is 0 at the goal
        return [(-1 * sum([prob * np.log(prob) for prob in probs_posterior[g][a].values()])) for a in path[:-1]]

    entropies_prior = paths_no_backtrack.apply(prior_entropies_along_path)
    entropies_posterior = paths_no_backtrack.apply(posterior_entropies_along_path)

    return entropies_prior, entropies_posterior


def information_gain(entropies_prior, entropies_posterior):
    # Define a function to subtract two lists element-wise
    def subtract_lists(list1, list2):
        return [a - b for a, b in zip(list1, list2)]

    # Subtract posterior entropy to prior entropy element-wise in each path to obtain information gain
    return entropies_prior.combine(entropies_posterior, subtract_lists)