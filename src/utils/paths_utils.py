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