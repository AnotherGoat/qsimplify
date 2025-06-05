import numpy

from qsimplify import math_utils
from qsimplify.model.edge_name import EdgeName
from qsimplify.model.gate_name import GateName
from qsimplify.model.position import Position
from qsimplify.model.quantum_graph import QuantumGraph


def clean_and_fill(graph: QuantumGraph) -> None:
    """Clean the provided graph, which removes empty rows, columns, adjusts bit indices, and also fills up any empty spaces."""
    _remove_empty_rows(graph)
    _remove_empty_columns(graph)
    _normalize_rotation_angles(graph)
    _remove_unused_bits(graph)
    fill(graph)


def fill(graph: QuantumGraph) -> None:
    """Fill up empty spaces on the provided graph, without removing any empty rows, columns, or adjusting bit indices."""
    _fill_empty_spaces(graph)
    _fix_positional_edges(graph)


def _normalize_rotation_angles(graph: QuantumGraph) -> None:
    for node in [node for node in graph if node.name == GateName.P]:
        graph.remove_node(node.position)
        graph.add_node(node.name, node.position, angle=math_utils.normalize_angle(node.angle))

    for node in [node for node in graph if node.name.is_rotation()]:
        graph.remove_node(node.position)
        graph.add_node(
            node.name, node.position, angle=math_utils.normalize_angle(node.angle, 4 * numpy.pi)
        )

    for node in [node for node in graph if node.name == GateName.CP and node.angle is not None]:
        edges = graph.node_edge_data(node.position)
        control = edges.controlled_by[0].position
        target = node.position

        graph.remove_node(control)
        graph.remove_node(target)

        graph.add_node(GateName.CP, control)
        graph.add_node(GateName.CP, target, angle=math_utils.normalize_angle(node.angle))

        graph.add_edge(EdgeName.TARGETS, control, target)
        graph.add_edge(EdgeName.CONTROLLED_BY, target, control)


def _remove_empty_rows(graph: QuantumGraph) -> None:
    empty_rows = _find_empty_rows(graph)
    initial_height = graph.height

    for offset, row_index in enumerate(empty_rows):
        adjusted_row = row_index - offset

        for column_index in range(graph.width):
            graph.remove_node(Position(adjusted_row, column_index))

        for subsequent_row in range(adjusted_row + 1, initial_height):
            for column_index in range(graph.width):
                node_position = Position(subsequent_row, column_index)
                node = graph[node_position]

                if node is not None:
                    graph.move_node(
                        node_position,
                        Position(subsequent_row - 1, column_index),
                    )


def _find_empty_rows(graph: QuantumGraph) -> list[int]:
    empty_rows = []

    for row_index in range(graph.height):
        is_empty = True

        for column_index in range(graph.width):
            node = graph[Position(row_index, column_index)]

            if node is not None and node.name != GateName.ID:
                is_empty = False
                break

        if is_empty:
            empty_rows.append(row_index)

    return empty_rows


def _remove_empty_columns(graph: QuantumGraph) -> None:
    empty_columns = _find_empty_columns(graph)
    initial_width = graph.width

    for offset, column_index in enumerate(empty_columns):
        adjusted_column = column_index - offset

        for row_index in range(graph.height):
            graph.remove_node(Position(row_index, adjusted_column))

        for subsequent_column in range(adjusted_column + 1, initial_width):
            for row_index in range(graph.height):
                node_position = Position(row_index, subsequent_column)
                node = graph[node_position]

                if node is not None:
                    graph.move_node(
                        node_position,
                        Position(row_index, subsequent_column - 1),
                    )


def _find_empty_columns(graph: QuantumGraph) -> list[int]:
    empty_columns = []

    for column_index in range(graph.width):
        is_empty = True

        for row_index in range(graph.height):
            node = graph[Position(row_index, column_index)]

            if node is not None and node.name != GateName.ID:
                is_empty = False
                break

        if is_empty:
            empty_columns.append(column_index)

    return empty_columns


def _remove_unused_bits(graph: QuantumGraph) -> None:
    measure_nodes = [node for node in graph if node.name == GateName.MEASURE]
    original_values = {node.bit for node in measure_nodes}
    mappings = {original: new for new, original in enumerate(sorted(original_values))}

    for node in measure_nodes:
        position = node.position
        new_bit = mappings[node.bit]
        graph.remove_node(position)
        graph.add_node(GateName.MEASURE, position, bit=new_bit)


def _fill_empty_spaces(graph: QuantumGraph) -> None:
    for row in range(graph.height):
        for column in range(graph.width):
            position = Position(row, column)

            if graph.has_node_at(position):
                continue

            graph.add_node(GateName.ID, position)


def _fix_positional_edges(graph: QuantumGraph) -> None:
    _clear_positional_edges(graph)

    for row_index in range(graph.height):
        for column_index in range(graph.width):
            node_position = Position(row_index, column_index)
            adjacent_positions = _find_adjacent_positions(node_position)

            for direction, adjacent_position in adjacent_positions.items():
                if graph.has_node_at(adjacent_position):
                    graph.add_edge(direction, node_position, adjacent_position)


def _clear_positional_edges(graph: QuantumGraph) -> None:
    non_positional_edges = [edge for edge in graph.edges() if not edge.name.is_positional()]

    graph.clear_edges()

    for edge in non_positional_edges:
        graph.add_edge(edge.name, edge.start.position, edge.end.position)


def _find_adjacent_positions(position: Position) -> dict[EdgeName, Position]:
    row, column = position

    if column == 0:
        return {EdgeName.RIGHT: Position(row, column + 1)}

    return {
        EdgeName.LEFT: Position(row, column - 1),
        EdgeName.RIGHT: Position(row, column + 1),
    }
