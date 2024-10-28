from __future__ import annotations
from typing import Iterator
import networkx
from networkx.classes import MultiDiGraph

from qsimplify.model.position import Position
from qsimplify.model.gate_name import GateName
from qsimplify.model.edge_name import  EdgeName
from qsimplify.model.graph_node import GraphNode
from qsimplify.model.graph_edge import GraphEdge
from qsimplify.model.edge_data import EdgeData

_TARGETS = EdgeName.TARGETS
_CONTROLLED_BY = EdgeName.CONTROLLED_BY
_WORKS_WITH = EdgeName.WORKS_WITH

class QuantumGraph:
    """
    Represents a QuantumCircuit as a graph-grid hybrid.
    Position tuples of the form (row, column) are used to index the graph's nodes.
    Each qubit is represented by a row in the grid.
    Single-qubit gates occupy a single GraphNode, while multi-qubit gates use multiple related GraphNodes (one for each qubit involved).
    """

    def __init__(self):
        """Create an empty QuantumGraph."""
        self._network = MultiDiGraph()

    @property
    def width(self) -> int:
        """The number of columns in the graph."""
        if len(self) == 0:
            return 0

        return max(position[1] for position in self.get_positions()) + 1

    @property
    def height(self) -> int:
        """The number of rows (qubits) in the graph."""
        if len(self) == 0:
            return 0

        return max(position[0] for position in self.get_positions()) + 1

    def get_positions(self) -> Iterator[Position]:
        for position in self._network.nodes:
            yield position

    def add_node(self, node: GraphNode):
        """Add an existing GraphNode to the graph."""
        self._network.add_node(node.position, name=node.name, position=node.position, rotation=node.rotation, measure_to=node.measure_to)

    def add_new_node(self, name: GateName, position: Position, rotation: float = None, measure_to: int = None):
        """Add a new node to the graph."""
        self._network.add_node(position, name=name, position=position, rotation=rotation, measure_to=measure_to)

    def remove_node(self, position: Position):
        self._network.remove_node(position)

    def __getitem__(self, position: Position) -> GraphNode | None:
        """Get the GraphNode at the specified (row, column) Position."""
        if not self._network.has_node(position):
            return None

        node = self._network.nodes[position]
        return GraphNode(node["name"], node["position"], rotation=node["rotation"], measure_to=node["measure_to"])

    def __iter__(self) -> Iterator[GraphNode]:
        """Iterate over the nodes in the graph."""
        for _, data in self._network.nodes(data=True):
            yield GraphNode(data["name"], data["position"], rotation=data["rotation"], measure_to=data["measure_to"])

    def nodes(self) -> list[GraphNode]:
        """Retrieve all the nodes in the graph."""
        return [node for node in self]

    def add_edge(self, edge: GraphEdge):
        """Add an existing GraphEdge to the graph."""
        self._network.add_edge(edge.start.position, edge.end.position, name=edge.name)

    def add_new_edge(self, name: EdgeName, start: Position, end: Position):
        """Add a new edge to the graph."""
        self._network.add_edge(start, end, name=name)

    def iter_edges(self) -> Iterator[GraphEdge]:
        """Iterate over the edges in the graph."""
        for start, end, data in self._network.edges(data=True):
            yield GraphEdge(data["name"], self[start], self[end])

    def edges(self) -> list[GraphEdge]:
        """Retrieve all the edges in the graph."""
        return [edge for edge in self.iter_edges()]

    def iter_node_edges(self, row: int, column: int) -> Iterator[GraphEdge]:
        start = (row, column)

        for _, end, data in self._network.out_edges(start, data=True):
            yield GraphEdge(data["name"], self[start], self[end])

    def node_edges(self, row: int, column: int) -> list[GraphEdge]:
        return [edge for edge in self.iter_node_edges(row, column)]

    def node_edge_data(self, row: int, column: int) -> EdgeData | None:
        start = (row, column)
        origin = self[start]

        if origin is None:
            return None

        edge_data = {
            _TARGETS.value: [],
            _CONTROLLED_BY.value: [],
            _WORKS_WITH.value: []
        }

        for _, end, data in self._network.out_edges(start, data=True):
            edge_name = data["name"]
            destination_node = self[end]

            if edge_name in [_TARGETS, _CONTROLLED_BY, _WORKS_WITH]:
                edge_data[edge_name.value].append(destination_node)
            else:
                edge_data[edge_name.value] = destination_node

        return EdgeData(origin, **edge_data)

    def __str__(self):
        result = ["Nodes:"]
        result += [str(node) for node in self]
        result += ["\nEdges:"]
        result += [str(edge) for edge in self.edges()]
        return "\n".join(result)

    def draw_grid(self):
        grid = [[GateName.ID.value for _ in range(self.width)] for _ in range(self.height)]

        for position in self.get_positions():
            row, column = position
            grid[row][column] = self[position].name.value

        transposed_grid = zip(*grid)
        column_lengths = []

        for column in transposed_grid:
            max_text_length = max(len(str(node)) for node in column)
            column_lengths.append(max_text_length)

        rows = []

        for row_index, row in enumerate(grid):
            formatted_values = [
                f"{str(value):<{max_text_length}}"
                for value, max_text_length in zip(row, column_lengths)
            ]

            row_data = "   ".join(formatted_values)
            rows.append(f"{row_index}: {row_data}")

        return "\n".join(rows)

    def __contains__(self, node: GraphNode) -> bool:
        return node.position in self._network

    def __eq__(self, other) -> bool:
        if not isinstance(other, QuantumGraph):
            return NotImplemented

        return networkx.utils.graphs_equal(self._network, other._network)

    def is_occupied(self, row: int, column: int) -> bool:
        """Check whether the graph has a non-filler node at the specified row and column."""
        return self.has_node_at(row, column) and self[row, column].name != GateName.ID

    def has_node_at(self, row: int, column: int) -> bool:
        """Check whether the graph has a node at the specified row and column."""
        return self._network.has_node((row, column))

    def fill_empty_spaces(self):
        for row_index in range(self.height):
            for column_index in range(self.width):
                if self.has_node_at(row_index, column_index):
                    continue

                self.add_new_node(GateName.ID, (row_index, column_index))

    def fill_positional_edges(self):
        self._clear_positional_edges()

        for row_index in range(self.height):
            for column_index in range(self.width):
                node_position = (row_index, column_index)
                adjacent_positions = self._find_adjacent_positions(row_index, column_index)

                for direction, (adjacent_row, adjacent_column) in adjacent_positions.items():
                    if self.has_node_at(adjacent_row, adjacent_column):
                        adjacent_position = (adjacent_row, adjacent_column)
                        self.add_new_edge(direction, node_position, adjacent_position)

    @staticmethod
    def _find_adjacent_positions(row_index: int, column_index: int) -> dict[EdgeName, Position]:
        return {
            EdgeName.LEFT: (row_index, column_index - 1),
            EdgeName.RIGHT: (row_index, column_index + 1)
        }

    def _clear_positional_edges(self):
        non_positional_edges = [edge for edge in self.edges() if not edge.name.is_positional()]

        self.clear_edges()

        for edge in non_positional_edges:
            self.add_edge(edge)

    def clear(self):
        """Remove all the nodes and edges from the graph."""
        self._network.clear()

    def clear_edges(self):
        """Remove all the edges from the graph."""
        self._network.clear_edges()

    def __len__(self):
        """Get the total number of nodes in the graph."""
        return len(self._network.nodes)

    def copy(self) -> QuantumGraph:
        copy = QuantumGraph()
        copy._network = self._network.copy()
        return copy
