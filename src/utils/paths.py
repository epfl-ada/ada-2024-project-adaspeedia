import collections


def paths_no_backtrack(paths):
    """
    Create simplified paths by getting rid of the backtracking steps, and going straight
    where the player ended up going after backtracking
    """

    def __straighten_path(path):
        """
        Get rid of the backtracikng steps in a single path
        """
        stack = collections.deque()
        for article in path:
            if article == '<':
                stack.pop()
            else:
                stack.append(article)
        return list(stack)

    return paths.apply(__straighten_path)

def get_pairs_with_defined_distance(paths_homing_in_humans):
    all_distance_pairs = set()
    all_articles = set()
    for path in paths_homing_in_humans:
        goal  = path[-1]
        for article in path:
            all_articles.add(article)
            all_distance_pairs.add((goal, article))
    return all_distance_pairs, all_articles