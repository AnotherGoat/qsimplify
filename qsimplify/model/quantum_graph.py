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
        if self.is_empty():
            return 0

        return max(position.column for position in self._get_positions()) + 1

    @property
    def height(self) -> int:
        """The number of rows (qubits) in the graph."""
        if self.is_empty():
            return 0

        return max(position.row for position in self._get_positions()) + 1

    @property
    def bits(self) -> int:
        """The number of classical bits in the graph."""
        measure_nodes = [node for node in self if node.name == GateName.MEASURE]

        if len(measure_nodes) == 0:
            return 0

        highest_bit = max(node.measure_to for node in measure_nodes)
        return highest_bit + 1

    def _get_positions(self) -> Iterator[Position]:
        for position in self._network.nodes:
            yield position

    def is_empty(self) -> bool:
        """Check whether this graph is empty (has no gates) or not."""
        return len(self) == 0

    def add_node(self, node: GraphNode) -> None:
        """Add an existing GraphNode to the graph."""
        self.add_new_node(node.name, node.position, node.rotation, node.measure_to)

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
            rotation=rotation,
            measure_to=measure_to,
        )

    def remove_node(self, position: Position) -> None:
        """Remove the GraphNode at the specified position and all its edges. If no such node exists, nothing happens."""
        if self.has_node_at(position):
            self._network.remove_node(position)

    def move_node(self, start: Position, end: Position) -> None:
        """Move the node at the specified position to another position, removing the node at the destination."""
        if not self.has_node_at(start):
            raise ValueError(f"Node at position {start} does not exist")

        if start == end:
            raise ValueError(f"Start and end positions shouldn't be the same {start}")

        node = self._network.nodes[start]
        in_edges = list(self._network.in_edges(start, data=True))
        out_edges = list(self._network.out_edges(start, data=True))

        self.remove_node(end)
        self.remove_node(start)
        self._network.add_node(end, **node)

        for source, _, data in in_edges:
            if source != start:
                self._network.add_edge(source, end, **data)

        for _, target, data in out_edges:
            if target != start:
                self._network.add_edge(end, target, **data)

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
            position,
            rotation=node["rotation"],
            measure_to=node["measure_to"],
        )

    def __iter__(self) -> Iterator[GraphNode]:
        """Iterate over the nodes in the graph."""
        for position, node in self._network.nodes(data=True):
            yield GraphNode(
                node["name"],
                position,
                rotation=node["rotation"],
                measure_to=node["measure_to"],
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

    def insert_column(self, column_index: int) -> None:
        """Insert an empty column at the given index by shifting all columns at or to the right of it rightward by one."""
        if self.is_empty():
            raise ValueError("It's not possible to insert a column on an empty graph")

        if column_index < 0 or column_index > self.width:
            raise ValueError(f"Column index {column_index} is out of bounds")

        for column in reversed(range(column_index, self.width)):
            for row in range(self.height):
                old_position = Position(row, column)
                new_position = Position(row, column + 1)

                if self.has_node_at(old_position):
                    self.move_node(old_position, new_position)

        for row in range(self.height):
            self.add_new_node(GateName.ID, Position(row, column_index))

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
