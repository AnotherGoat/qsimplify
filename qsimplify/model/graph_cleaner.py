from qsimplify.model.gate_name import GateName
from qsimplify.model.quantum_graph import QuantumGraph
from qsimplify.model.position import Position
from qsimplify.model.edge_name import EdgeName


def clean_and_fill(graph: QuantumGraph) -> None:
    """Clean the provided graph, which removes empty rows and columns, and also fills up any empty spaces."""
    _remove_empty_rows(graph)
    _remove_empty_columns(graph)
    fill(graph)


def fill(graph: QuantumGraph) -> None:
    """Fill up empty spaces on the provided graph, without removing any empty rows or columns."""
    _fill_empty_spaces(graph)
    _fix_positional_edges(graph)


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

def _fill_empty_spaces(graph: QuantumGraph) -> None:
    for row in range(graph.height):
        for column in range(graph.width):
            position = Position(row, column)

            if graph.has_node_at(position):
                continue

            graph.add_new_node(GateName.ID, position)


def _fix_positional_edges(graph: QuantumGraph) -> None:
    _clear_positional_edges(graph)

    for row_index in range(graph.height):
        for column_index in range(graph.width):
            node_position = Position(row_index, column_index)
            adjacent_positions = _find_adjacent_positions(node_position)

            for direction, adjacent_position in adjacent_positions.items():
                if graph.has_node_at(adjacent_position):
                    graph.add_new_edge(direction, node_position, adjacent_position)

def _clear_positional_edges(graph: QuantumGraph) -> None:
    non_positional_edges = [edge for edge in graph.edges() if not edge.name.is_positional()]

    graph.clear_edges()

    for edge in non_positional_edges:
        graph.add_edge(edge)

def _find_adjacent_positions(position: Position) -> dict[EdgeName, Position]:
    row, column = position

    if column == 0:
        return {EdgeName.RIGHT: Position(row, column + 1)}

    return {
        EdgeName.LEFT: Position(row, column - 1),
        EdgeName.RIGHT: Position(row, column + 1),
    }
