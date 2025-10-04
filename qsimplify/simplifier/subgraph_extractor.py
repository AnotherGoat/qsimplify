from typing import assert_never

from loguru import logger

from qsimplify.model import GateName, GraphNode, Position, QuantumGraph, graph_cleaner
from qsimplify.simplifier.pattern_match import PatternMatch
from qsimplify.simplifier.position_mask import PositionMask


def extract_subgraph(
    graph: QuantumGraph,
    rows: list[int],
    starting_column: int,
    width: int,
    mask: PositionMask | None = None,
) -> tuple[QuantumGraph | None, PatternMatch | None]:
    """Extract a subgraph from a bigger graph.

    It starts from the specified starting column and always goes to the right from there.
    The extracted rows can be in any order, depending on the passed parameter.

    Parameters:
        graph: The graph to extract the subgraph from.
        rows: The rows to extract, in the specified order from top to bottom.
        starting_column: The column to start extracting from.
        width: The width of the extracted subgraph.
        mask: A mask that specifies which nodes should be extracted. If not specified, all the nodes will be extracted.
    """
    if len(rows) == 0 or width <= 0 or graph.is_empty():
        raise ValueError("The graph, rows or width are invalid")

    if mask is None:
        mask = _generate_full_mask(width, len(rows))

    mappings = _extract_subgraph_mappings(graph, rows, starting_column, width, mask)
    logger.debug("Extracting mappings for width {}", width)

    if mappings is None:
        logger.debug("Mappings couldn't be extracted")
        return None, None

    subgraph = QuantumGraph()

    for old_position, new_position in mappings.items():
        node = graph[old_position]

        if node is None:
            assert_never(node)

        subgraph.add_node(
            node.name,
            new_position,
            angle=node.angle,
            bit=node.bit,
        )

        edges = [edge for edge in graph.node_edges(old_position) if not edge.name.is_positional()]
        for edge in edges:
            subgraph.add_edge(
                edge.name,
                mappings[edge.start.position],
                mappings[edge.end.position],
            )

    logger.debug("Mappings are valid, filling the subgraph")
    graph_cleaner.clean_and_fill(subgraph)
    return subgraph, mappings


def _generate_full_mask(width: int, height: int) -> PositionMask:
    mask_data = {}

    for row in range(height):
        for column in range(width):
            position = Position(row, column)
            mask_data[position] = True

    return PositionMask(mask_data)


def _extract_subgraph_mappings(
    graph: QuantumGraph,
    rows: list[int],
    starting_column: int,
    width: int,
    mask: PositionMask,
) -> PatternMatch | None:
    mappings: PatternMatch = {}
    logger.debug("Starting mapping extraction")

    for new_row, old_row in enumerate(rows):
        new_column = 0
        old_column = starting_column

        while True:
            if new_column == width:
                break

            logger.debug(
                "Trying to map {} into {}",
                Position(old_row, old_column),
                Position(new_row, new_column),
            )
            node = _find_next_right_node(
                graph,
                Position(old_row, old_column),
                not mask.is_set(Position(new_row, new_column)),
            )

            if node is None:
                logger.debug("No node found at the right side")
                return None

            mappings[node.position] = Position(new_row, new_column)
            logger.debug("Mappings updated to {}", mappings)
            old_column = node.position.column + 1
            new_column += 1

    for old_position in mappings:
        edges = [edge for edge in graph.node_edges(old_position) if not edge.name.is_positional()]

        for edge in edges:
            if edge.end.position not in mappings:
                return None

    return mappings


def _find_next_right_node(
    graph: QuantumGraph,
    start: Position,
    can_be_identity: bool,
) -> GraphNode | None:
    edge_data = graph.node_edge_data(start)
    logger.debug("Going to the right starting from edge {}", edge_data)
    logger.debug("Can it be identity? {}", can_be_identity)

    if edge_data is None:
        logger.debug("No edge data found at position {}", start)
        return None

    while True:
        origin = edge_data.origin

        if can_be_identity or origin.name != GateName.ID:
            logger.debug("The origin {} can be accepted, finishing exploration", origin)
            return origin

        right_edge = edge_data.right

        if right_edge is None:
            logger.debug("Reached the rightmost node, no origin found")
            return None

        edge_data = graph.node_edge_data(right_edge.position)

        if edge_data is None:
            assert_never(edge_data)
