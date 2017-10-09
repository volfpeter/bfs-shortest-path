"""
Test and demo script for the BFS shortest path implementation.
"""

# Imports
# ------------------------------------------------------------

from typing import List

import random
import time
import unittest

from igraph import EdgeSeq, Graph, InternalError

from bfs_shortest_path import shortest_path

# Module constants
# ------------------------------------------------------------

__author__ = "Peter Volf"

# Content
# ------------------------------------------------------------


def create_random_weighted_Erdos_Renyi_graph(n: int, p: float) -> Graph:
    """
    Creates an Erdos-Renyi random graph with the specified parameters and
    assigns random positive weight to the edges of the graph.

    Arguments:
        n (int): The number of nodes in the graph.
        p (float): The probability of two nodes being connected.

    Returns:
        A weighted Erdos-Renyi graph.
    """
    graph: Graph = Graph.Erdos_Renyi(n=n, p=p)
    for edge in graph.es:
        edge["weight"] = 1 + random.random()

    return graph


def create_negative_edges(graph: Graph, negative_count: int) -> None:
    """
    Creates the given number of negative weight edges in the graph without
    creating a negative circle if it is possible.

    Arguments:
        graph (Graph): The graph to create negative edges in.
        negative_count (int): The number of negative edges the graph should have.
    """
    if negative_count <= 0:
        return

    edges: EdgeSeq = graph.es
    edge_indices: List[int] = list(range(len(graph.es)))
    random.shuffle(edge_indices)

    while negative_count > 0 and len(edge_indices) > 0:
        index: int = edge_indices.pop()
        try:
            edges[index]["weight"] *= -0.5
            graph.shortest_paths(0, None, "weight")

            # No negative circle was created.
            negative_count -= 1
        except InternalError:
            # Negative circle was created, undo the weight inversion.
            edges[index]["weight"] *= -2


class BFSShortestPathTest(unittest.TestCase):

    small_test_fixtures = [
        (20, 0.7, 0), (20, 0.7, 1), (20, 0.7, 2),
        (20, 0.8, 0), (20, 0.8, 1), (20, 0.8, 2),
        (20, 0.9, 0), (20, 0.9, 1), (20, 0.9, 2),
        (40, 0.65, 0), (40, 0.65, 3), (40, 0.65, 5),
        (40, 0.75, 0), (40, 0.75, 3), (40, 0.75, 5),
        (40, 0.85, 0), (40, 0.85, 3), (40, 0.85, 5),
        (70, 0.6, 0), (70, 0.6, 4), (70, 0.6, 7),
        (70, 0.75, 0), (70, 0.75, 4), (70, 0.75, 7),
        (70, 0.85, 0), (70, 0.85, 4), (70, 0.85, 7)
    ]

    large_test_fixtures = [
        (120, 0.5, 0), (120, 0.5, 5), (120, 0.5, 10),
        (120, 0.65, 0), (120, 0.65, 5), (120, 0.65, 10),
        (120, 0.85, 0), (120, 0.85, 5), (120, 0.85, 10),
        (200, 0.5, 0), (200, 0.5, 6), (200, 0.5, 12),
        (200, 0.65, 0), (200, 0.65, 6), (200, 0.65, 12),
        (200, 0.85, 0), (200, 0.85, 6), (200, 0.85, 12),
        (500, 0.5, 0), (500, 0.5, 8), (500, 0.5, 14),
        (500, 0.65, 0), (500, 0.65, 8), (500, 0.65, 14),
        (500, 0.85, 0), (500, 0.85, 8), (500, 0.85, 14)
    ]

    def execute_shortest_path_with(self, n: int, p: float, negative_count: int) -> None:
        """
        Tests the BFS shortest path finding algorithm with an Erdos-Renyi graph
        created with the specified parameters.

        Arguments:
            n (int): The number of nodes in the graph.
            p (float): The probability of two nodes being connected.
            negative_count (int): The number of negative edges the graph should have.
        """
        print("Testing with n={}, p={}, negative_count={}".format(n, p, negative_count))

        igraph_time: float = 0
        bfs_time: float = 0

        print("  - Graph creation...")
        graph: Graph = create_random_weighted_Erdos_Renyi_graph(n=n, p=p)
        create_negative_edges(graph, negative_count=negative_count)

        print("  - Comparing the igraph shortest_paths() implementation "
              "with the BFS shortest_path() implementation.")
        for node_index in range(n):
            start = time.time()
            igraph_shortest_paths = graph.shortest_paths(node_index, None, "weight")[0]
            igraph_time += time.time() - start

            start = time.time()
            shortest_paths = shortest_path(graph, node_index)
            bfs_time += time.time() - start

            for i in range(n):
                if igraph_shortest_paths[i] is None:
                    if shortest_paths[i] is not None:
                        self.fail("    ! None vs not None mismatch at {}".format(i))
                elif abs(igraph_shortest_paths[i] - shortest_paths[i]) > 10e-9:
                    self.fail("    ! Value mismatch: {} vs {}".format(igraph_shortest_paths[i], shortest_paths[i]))

        print("  - Total time used by igraph: {}ms".format(igraph_time))
        print("  - Total time used by BFS: {}ms".format(bfs_time))

    def test_small_fixtures(self):
        """
        Tests the shortest path findinf algorithm with small graphs.
        """
        for fixture in BFSShortestPathTest.small_test_fixtures:
            self.execute_shortest_path_with(*fixture)

    def test_large_fixtures(self):
        """
        Tests the shortest path findinf algorithm with small graphs.
        """
        for fixture in BFSShortestPathTest.large_test_fixtures:
            self.execute_shortest_path_with(*fixture)


if __name__ == "__main__":
    unittest.main()
