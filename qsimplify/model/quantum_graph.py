from __future__ import annotations

from typing import Iterator

import networkx
from networkx.classes import DiGraph

from qsimplify.model.edge_data import EdgeData
from qsimplify.model.edge_name import EdgeName
from qsimplify.model.gate_name import GateName
from qsimplify.model.graph_edge import GraphEdge
from qsimplify.model.graph_node import GraphNode
from qsimplify.model.position import Position


class QuantumGraph:
    """
    Represents a QuantumCircuit as a graph-grid hybrid.
    Position tuples of the form (row, column) are used to index the graph's nodes.
    Each qubit is represented by a row in the grid.
    Single-qubit gates occupy a single GraphNode, while multi-qubit gates use multiple related GraphNodes (one for each qubit involved).
    """

    def __init__(self) -> None:
        """Create an empty QuantumGraph."""
        self._network = DiGraph()

    @property
    def width(self) -> int:
        """The number of columns in the graph."""
        if len(self) == 0:
            return 0

        return max(position.column for position in self._get_positions()) + 1

    @property
    def height(self) -> int:
        """The number of rows (qubits) in the graph."""
        if len(self) == 0:
            return 0

        return max(position.row for position in self._get_positions()) + 1

    def _get_positions(self) -> Iterator[Position]:
        for position in self._network.nodes:
            yield position

    def add_node(self, node: GraphNode) -> None:
        """Add an existing GraphNode to the graph."""
        self._network.add_node(
            node.position,
            name=node.name,
            position=node.position,
            rotation=node.rotation,
            measure_to=node.measure_to,
        )

    def add_new_node(
        self,
        name: GateName,
        position: Position,
        rotation: float | None = None,
        measure_to: int | None = None,
    ) -> None:
        """Add a new node to the graph."""
        self._network.add_node(
            position,
            name=name,
            position=position,
            rotation=rotation,
            measure_to=measure_to,
        )

    def remove_node(self, position: Position) -> None:
        """Remove the GraphNode at the specified position and all its edges."""
        if self.has_node_at(position):
            self._network.remove_node(position)

    def move_node(self, start: Position, end: Position) -> None:
        pass

    def clear_node(self, position: Position) -> None:
        """Replace the GraphNode at the specified position with an identity node."""
        self.remove_node(position)
        self.add_new_node(GateName.ID, position)

    def __getitem__(self, position: Position) -> GraphNode | None:
        """Get the GraphNode at the specified position."""
        if not self.has_node_at(position):
            return None

        node = self._network.nodes[position]
        return GraphNode(
            node["name"],
            node["position"],
            rotation=node["rotation"],
            measure_to=node["measure_to"],
        )

    def __iter__(self) -> Iterator[GraphNode]:
        """Iterate over the nodes in the graph."""
        for _, data in self._network.nodes(data=True):
            yield GraphNode(
                data["name"],
                data["position"],
                rotation=data["rotation"],
                measure_to=data["measure_to"],
            )

    def iter_positions_by_row(self) -> Iterator[Position]:
        """
        Iterate over the graph's positions, first row by row and then column by column.
        In case some spaces are empty, they will be skipped.
        """
        for row in range(self.height):
            for column in range(self.width):
                position = Position(row, column)

                if self.has_node_at(position):
                    yield position

    def iter_positions_by_column(self) -> Iterator[Position]:
        """
        Iterate over the graph's positions, first column by column and then row by row.
        In case some spaces are empty, they will be skipped.
        """
        for column in range(self.width):
            for row in range(self.height):
                position = Position(row, column)

                if self.has_node_at(position):
                    yield position

    def nodes(self) -> list[GraphNode]:
        """Retrieve all the nodes in the graph."""
        return list(self)

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an existing GraphEdge to the graph."""
        self._network.add_edge(edge.start.position, edge.end.position, name=edge.name)

    def add_new_edge(self, name: EdgeName, start: Position, end: Position) -> None:
        """Add a new edge to the graph."""
        self._network.add_edge(start, end, name=name)

    def iter_edges(self) -> Iterator[GraphEdge]:
        """Iterate over the edges in the graph."""
        for start, end, data in self._network.edges(data=True):
            yield GraphEdge(data["name"], self[start], self[end])

    def edges(self) -> list[GraphEdge]:
        """Retrieve all the edges in the graph."""
        return list(self.iter_edges())

    def iter_node_edges(self, position: Position) -> Iterator[GraphEdge]:
        for _, end, data in self._network.out_edges(position, data=True):
            yield GraphEdge(data["name"], self[position], self[end])

    def node_edges(self, position: Position) -> list[GraphEdge]:
        return list(self.iter_node_edges(position))

    def node_edge_data(self, position: Position) -> EdgeData | None:
        origin = self[position]

        if origin is None:
            return None

        edge_data = {
            EdgeName.TARGETS.value: [],
            EdgeName.CONTROLLED_BY.value: [],
            EdgeName.WORKS_WITH.value: [],
        }

        for _, end, data in self._network.out_edges(position, data=True):
            edge_name = data["name"]
            destination_node = self[end]

            if edge_name in [
                EdgeName.TARGETS,
                EdgeName.CONTROLLED_BY,
                EdgeName.WORKS_WITH,
            ]:
                edge_data[edge_name.value].append(destination_node)
            else:
                edge_data[edge_name.value] = destination_node

        return EdgeData(origin, **edge_data)

    def __str__(self) -> str:
        result = ["Nodes:"]
        result += [str(node) for node in self]
        result += ["\nEdges:"]
        result += [str(edge) for edge in self.edges()]
        return "\n".join(result)

    def draw_grid(self) -> str:
        grid = [[GateName.ID.value for _ in range(self.width)] for _ in range(self.height)]

        for position in self._get_positions():
            row, column = position
            grid[row][column] = self[position].name.value

        transposed_grid = zip(*grid, strict=False)
        column_lengths = []

        for column in transposed_grid:
            max_text_length = max(len(str(node)) for node in column)
            column_lengths.append(max_text_length)

        rows = []

        for row_index, row in enumerate(grid):
            formatted_values = [
                f"{value!s:<{max_text_length}}"
                for value, max_text_length in zip(row, column_lengths, strict=False)
            ]

            row_data = "   ".join(formatted_values)
            rows.append(f"{row_index}: {row_data}")

        return "\n".join(rows)

    def __contains__(self, node: GraphNode) -> bool:
        return node.position in self._network

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QuantumGraph):
            return NotImplemented

        return networkx.utils.graphs_equal(self._network, other._network)

    def is_occupied(self, position: Position) -> bool:
        """Check whether the graph has a non-filler node at the specified row and column."""
        return self.has_node_at(position) and self[position].name != GateName.ID

    def has_node_at(self, position: Position) -> bool:
        """Check whether the graph has a node at the specified row and column."""
        return position in self._network

    def clean_up(self) -> None:
        """Clean up this graph, which removes empty rows and columns, and also fills up any empty spaces."""
        self.remove_empty_rows()
        self.remove_empty_columns()
        self.fill_empty_spaces()
        self.fill_positional_edges()

    def remove_empty_rows(self) -> None:
        pass

    def remove_empty_columns(self) -> None:
        empty_columns = self._find_empty_columns()
        print(empty_columns)
        initial_width = self.width

        for offset, column_index in enumerate(empty_columns):
            adjusted_column = column_index - offset

            for row_index in range(self.height):
                self.remove_node(Position(row_index, adjusted_column))

            for subsequent_column in range(adjusted_column + 1, initial_width):
                for row_index in range(self.height):
                    node_position = Position(row_index, subsequent_column)
                    node = self[node_position]

                    if node is not None:
                        self.move_node(
                            node_position,
                            Position(row_index, subsequent_column - 1),
                        )

    def _find_empty_columns(self) -> list[int]:
        empty_columns = []

        for column_index in range(self.width):
            is_empty = True

            for row_index in range(self.height):
                node = self[Position(row_index, column_index)]

                if node is not None and node.name != GateName.ID:
                    is_empty = False
                    break

            if is_empty:
                empty_columns.append(column_index)

        return empty_columns

    def fill_empty_spaces(self) -> None:
        for row in range(self.height):
            for column in range(self.width):
                position = Position(row, column)

                if self.has_node_at(position):
                    continue

                self.add_new_node(GateName.ID, position)

    def fill_positional_edges(self) -> None:
        self._clear_positional_edges()

        for row_index in range(self.height):
            for column_index in range(self.width):
                node_position = Position(row_index, column_index)
                adjacent_positions = self._find_adjacent_positions(node_position)

                for direction, adjacent_position in adjacent_positions.items():
                    if self.has_node_at(adjacent_position):
                        self.add_new_edge(direction, node_position, adjacent_position)

    @staticmethod
    def _find_adjacent_positions(position: Position) -> dict[EdgeName, Position]:
        row, column = position

        if column == 0:
            return {EdgeName.RIGHT: Position(row, column + 1)}

        return {
            EdgeName.LEFT: Position(row, column - 1),
            EdgeName.RIGHT: Position(row, column + 1),
        }

    def _clear_positional_edges(self) -> None:
        non_positional_edges = [edge for edge in self.edges() if not edge.name.is_positional()]

        self.clear_edges()

        for edge in non_positional_edges:
            self.add_edge(edge)

    def clear(self) -> None:
        """Remove all the nodes and edges from the graph."""
        self._network.clear()

    def clear_edges(self) -> None:
        """Remove all the edges from the graph."""
        self._network.clear_edges()

    def __len__(self) -> int:
        """Get the total number of nodes in the graph."""
        return len(self._network.nodes)

    def copy(self) -> QuantumGraph:
        copy = QuantumGraph()
        copy._network = self._network.copy()
        return copy
