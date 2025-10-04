"""Contains functions that try to match a patterns against graphs."""

import itertools

from loguru import logger

from qsimplify import math_utils
from qsimplify.model import GraphNode, QuantumGraph
from qsimplify.simplifier import subgraph_extractor
from qsimplify.simplifier.pattern_match import PatternMatch
from qsimplify.simplifier.position_mask import PositionMask
from qsimplify.simplifier.quantum_pattern import QuantumPattern


def match_pattern(
    pattern: QuantumPattern, graph: QuantumGraph, mask: PositionMask | None = None
) -> PatternMatch | None:
    """Try to match a pattern against the graph.

    Returns None if no match was found.
    """
    for node in graph.iter_nodes_by_column():
        logger.debug("Checking graph on position {}", node.position)

        if not _are_nodes_similar(node, pattern.start):
            logger.debug(
                "No similarities found when comparing {} and {}",
                node,
                pattern.start,
            )
            continue

        match = _match_pattern(pattern, graph, node, mask=mask)

        if match is not None:
            return match

    return None


def _are_nodes_similar(first: GraphNode, second: GraphNode) -> bool:
    """Check whether two nodes are similar enough to start the pattern matching process."""
    return (
        first.name == second.name
        and _are_angles_similar(first.angle, second.angle)
        and first.bit == second.bit
    )


def _are_angles_similar(first: float | None, second: float | None) -> bool:
    """Check whether two optional angles are close enough to be considered equal."""
    if first is None and second is None:
        return True

    if first is None or second is None:
        return False

    return math_utils.are_floats_similar(first, second)


def _match_pattern(
    pattern: QuantumPattern,
    graph: QuantumGraph,
    start: GraphNode,
    mask: PositionMask | None = None,
) -> PatternMatch | None:
    for row_permutation in _calculate_row_permutations(pattern, graph, start):
        logger.debug("Trying row permutation {} on start {}", row_permutation, start)
        subgraph, match = subgraph_extractor.extract_subgraph(
            graph, row_permutation, start.position.column, pattern.width, mask=mask
        )

        if subgraph is not None and subgraph == pattern:
            logger.debug("Match found: {}", match)
            return match

    logger.debug("No matches found")
    return None


def _calculate_row_permutations(
    pattern: QuantumPattern, graph: QuantumGraph, start: GraphNode
) -> list[list[int]]:
    row = start.position.row

    if pattern.height == 1:
        return [[row]]

    other_rows = [row_index for row_index in range(graph.height) if row_index != row]
    permutations = [
        list(permutation) for permutation in itertools.permutations(other_rows, pattern.height - 1)
    ]

    for permutation in permutations:
        permutation.insert(pattern.start.position.row, row)

    return permutations
