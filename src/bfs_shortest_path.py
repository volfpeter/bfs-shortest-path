"""
Naive implementation of a breadth-first search and path fixing based shortest path finding algorithm.

The benefit of the BFS-based approach is that the algorithm is simple and yet it works even
with graphs that have negative edge weights (negative circles are obviously not allowed).
"""

# Imports
# ------------------------------------------------------------

from typing import Dict, Set

from igraph import EdgeSeq, Graph

# Module constants
# ------------------------------------------------------------

__author__ = "Peter Volf"

# Content
# ------------------------------------------------------------


def shortest_path(graph: Graph, source_index: int) -> Dict[int, float]:
    """
    Calculates the shortest paths in the given graph from the node specified
    by the given index to all other nodes in the graph.

    This implementation requires the edges of the graph to have a `weight` property.

    Arguments:
        graph (Graph): The graph to find shortest paths in.
        source_index (int): The index of the node to find shortest paths from.

    Returns:
        A dictionary whose keys are the node indices and whose values are the
        distances from source node to the corresponding node.
    """

    def _fix_distances() -> None:
        """
        Fixes the already calculated shortest paths that pass through the given nodes.
        """
        edges: EdgeSeq = graph.es

        while len(fix) > 0:
            node_index: int = fix.pop()
            base_distance = distances[node_index]

            for neighbor_index in graph.neighbors(node_index, "out"):
                if distances.get(neighbor_index) is None:
                    continue

                distance: float = base_distance + edges[graph.get_eid(node_index, neighbor_index)]["weight"]
                if distance < distances[neighbor_index]:
                    distances[neighbor_index] = distance
                    if neighbor_index in processed:
                        fix.add(neighbor_index)

    def _visit_neighbors() -> None:
        """
        Takes the next step in the breadth-first search and calculates the distances of the next
        batch of nodes from the source node.
        """
        edges: EdgeSeq = graph.es

        while len(check) > 0:
            node_index: int = check.pop()
            new_processed.add(node_index)
            base_distance = distances[node_index]

            for neighbor_index in graph.neighbors(node_index, "out"):
                if distances.get(neighbor_index) is None:
                    distances[neighbor_index] =\
                        base_distance + edges[graph.get_eid(node_index, neighbor_index)]["weight"]
                    check_next.add(neighbor_index)
                else:
                    distance = base_distance + edges[graph.get_eid(node_index, neighbor_index)]["weight"]
                    if distance < distances[neighbor_index]:
                        distances[neighbor_index] = distance
                        if neighbor_index in processed:
                            fix.add(neighbor_index)

        processed.update(new_processed)
        new_processed.clear()

    check: Set[int] = set()
    check_next: Set[int] = set()
    distances: Dict[int, float] = {source_index: 0}
    fix: Set[int] = set()
    new_processed: Set[int] = set()
    processed: Set[int] = set()

    check.add(source_index)

    # Start with a BFS step (no need for distance fixing after this step obviously).
    _visit_neighbors()
    check, check_next = check_next, check  # The two sets must be swapped after _visit_neighbors().

    # Move on to the BFS step + distance fixing loop.
    while len(fix) > 0 or len(check) > 0:
        _visit_neighbors()  # BFS step
        check, check_next = check_next, check  # The two sets must be swapped after _visit_neighbors().
        _fix_distances()  # PAth fixing step.

    return distances
