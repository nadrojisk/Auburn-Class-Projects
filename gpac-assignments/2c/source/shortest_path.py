""" Shortest path module. Finds the shortest path between a given source cell to a destination cell.

Modified code based on https://www.geeksforgeeks.org/shortest-path-in-a-binary-maze/
"""

from collections import deque
from functools import lru_cache
import gpac


class queueNode:
    """ A data structure for queue used in BFS. """

    def __init__(self, pt: tuple, dist: int):
        self.pt = pt  # The cordinates of the cell
        self.dist = dist  # Cell's distance from the source


def isValid(row: int, col: int, mat):
    """ Check whether given cell(row,col) is a valid cell or not. """

    return (0 <= row < len(mat)) and (0 <= col < len(mat[0]))


@lru_cache(maxsize=1000)
def BFS(mat, src: tuple, dest: tuple):
    """ Function to find the shortest path between a given source cell to a destination cell.
    """

    # if source or destination cell equals wall quit
    if mat[src[0]][src[1]] == gpac.WALL or mat[dest[0]][dest[1]] == gpac.WALL:
        return -1

    visited = [[False for i in range(len(mat[0]))] for j in range(len(mat))]

    # Mark the source cell as visited
    visited[src[0]][src[1]] = True

    # Create a queue for BFS
    queue = deque()

    # Distance of source cell is 0
    source_node = queueNode(src, 0)
    queue.append(source_node)  # Enqueue source cell

    # Do a BFS starting from source cell
    while queue:

        curr = queue.popleft()  # Dequeue the front cell

        # If we have reached the destination cell,
        # we are done
        pt = curr.pt
        if pt[0] == dest[0] and pt[1] == dest[1]:
            return curr.dist

        # These arrays are used to get row and column
        # numbers of 4 neighbors of a given cell
        row_num = [-1, 0, 0, 1]
        col_num = [0, -1, 1, 0]

        # Otherwise enqueue its adjacent cells
        for i in range(4):
            row = pt[0] + row_num[i]
            col = pt[1] + col_num[i]

            # if adjacent cell is valid, has path
            # and not visited yet, enqueue it.
            if (isValid(row, col, mat) and mat[row][col] != gpac.WALL and not visited[row][col]):
                visited[row][col] = True
                adj_cell = queueNode((row, col),
                                     curr.dist + 1)
                queue.append(adj_cell)

    # Return -1 if destination cannot be reached
    return -1
