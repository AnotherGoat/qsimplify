"""Contains functions that replace patterns in graphs, by providing pattern matches."""

from typing import assert_never

from loguru import logger

from qsimplify.model import QuantumGraph, graph_cleaner
from qsimplify.simplifier.pattern_match import PatternMatch


def replace_pattern(graph: QuantumGraph, replacement: QuantumGraph, match: PatternMatch) -> None:
    """Modify a graph by replacing part of it with another graph.

    The replacement graph should be smaller or the same size as the original graph.

    Parameters:
        graph: The graph to replace the pattern in.
        replacement: The pattern to put in the graph.
        match: An object that indicates where each pattern node should go in the graph.
    """
    logger.debug("Removing nodes with match {}", match)

    for original_position in match:
        graph.clear_node(original_position)

    match = {key: value for key, value in match.items() if value is not None}
    reverse_match = _invert_match(match)
    logger.debug("Reversed match is {}", reverse_match)

    for original, mapping in match.items():
        node = replacement[mapping]

        if node is None:
            assert_never(node)

        graph.add_node(node.name, original, angle=node.angle, bit=node.bit)

        for edge in replacement.node_edges(mapping):
            if edge.name.is_positional():
                continue

            graph.add_edge(edge.name, original, reverse_match[edge.end.position])

    graph_cleaner.clean_and_fill(graph)


def _invert_match(match: PatternMatch) -> PatternMatch:
    return {value: key for key, value in match.items()}
