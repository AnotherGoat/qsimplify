from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias, Tuple, Iterator
import networkx
from networkx.classes import MultiDiGraph
import textwrap

class GateName(Enum):
    ID = "id"
    H = "h"
    X = "x"
    Y = "y"
    Z = "z"
    RX = "rx"
    RY = "ry"
    RZ = "rz"
    SWAP = "swap"
    CH = "ch"
    CX = "cx"
    CZ = "cz"
    CSWAP = "cswap"
    CCX = "ccx"
    MEASURE = "measure"
    BARRIER = "barrier"
    BLOCKED = "|"

    @classmethod
    def from_str(cls, name: str):
        try:
            return cls(name.lower())
        except ValueError:
            raise ValueError(f"'{name}' is not a valid GateName")


Position: TypeAlias = Tuple[int, int]
"""Represents a (row, column) position in a QuantumGraph."""


class GraphNode:
    """
    Represents a node of a QuantumGraph.

    Attributes:
        name (GateName): The name of quantum gate represented by this node.
        position (Position): The position of this node in the graph.
    """
    def __init__(self, name: GateName, position: Position, measure_to: int = None, rotation: float = None):
        if position[0] < 0 or position[1] < 0:
            raise ValueError(f"GateNode position '{position}' can't have negative values")

        self.name = name
        self.position = position
        self.measure_to = measure_to
        self.rotation = rotation

    def __eq__(self, other) -> bool:
        if not isinstance(other, GraphNode):
            return NotImplemented

        return self.name == other.name and self.position == other.position and self.measure_to == other.measure_to and self.rotation == other.rotation

    def __str__(self):
        measure_to_data = f" (measure_to={self.measure_to})" if self.measure_to else ""
        rotation_data = f" (rotation={self.rotation})" if self.rotation else ""
        return f"{self.name.value} at {self.position}{measure_to_data}{rotation_data}"


class EdgeName(Enum):
    UP = "up"
    DOWN = "down"
    RIGHT = "right"
    LEFT = "left"
    SWAPS_WITH = "swaps_with"
    TARGETS = "targets"
    CONTROLLED_BY = "controlled_by"
    WORKS_WITH = "works_with"

    def is_positional(self):
        return self in (EdgeName.UP, EdgeName.DOWN, EdgeName.RIGHT, EdgeName.LEFT)


class GraphEdge:
    def __init__(self, name: EdgeName, start: GraphNode, end: GraphNode):
        self.name = name
        self.start = start
        self.end = end

    def __eq__(self, other) -> bool:
        if not isinstance(other, GraphEdge):
            return NotImplemented

        return self.name == other.name and self.start == other.start and self.end == other.end


    def __str__(self):
        return f"[{self.name.value}] from {self.start} to {self.end}"


class EdgeData:
    def __init__(
        self,
        origin: GraphNode,
        up: GraphNode = None,
        down: GraphNode = None,
        left: GraphNode = None,
        right: GraphNode = None,
        swaps_with: GraphNode = None,
        targets: list[GraphNode] = None,
        controlled_by: list[GraphNode] = None,
        works_with: list[GraphNode] = None,
    ):
        self.origin = origin
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        self.swaps_with = swaps_with
        self.targets = targets if targets is not None else []
        self.controlled_by = controlled_by if controlled_by is not None else []
        self.works_with = works_with if works_with is not None else []

    def __str__(self) -> str:
        target_names = [str(target) for target in self.targets]
        controller_names = [str(controller) for controller in self.controlled_by]
        works_with_names = [str(controller) for controller in self.works_with]
        extra_data = [
            f"up={self.up}" if self.up else "",
            f"down={self.down}" if self.down else "",
            f"left={self.left}" if self.left else "",
            f"right={self.right}" if self.right else "",
            f"swaps_with={self.swaps_with}" if self.swaps_with else "",
            f"targets={target_names}" if target_names else "",
            f"controlled_by={controller_names}" if controller_names else ""
            f"works_with={works_with_names}" if works_with_names else "",
        ]
        extra_data = [data for data in extra_data if data]

        if len(extra_data) == 0:
            return str(self.origin)

        return f"{self.origin}({', '.join(extra_data)})"


class QuantumGraph:
    """
    Represents a QuantumCircuit as a graph-grid hybrid.
    Position tuples of the form (row, column) are used to index the graph's nodes.
    Each qubit is represented by a row in the grid.
    Single-qubit gates occupy a single GraphNode, while multi-qubit gates use multiple related GraphNodes (one for each qubit involved).
    """
    _TARGETS = EdgeName.TARGETS
    _CONTROLLED_BY = EdgeName.CONTROLLED_BY
    _WORKS_WITH = EdgeName.WORKS_WITH

    def __init__(self):
        """Create an empty QuantumGraph."""
        self.network = MultiDiGraph()

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
        for position in self.network.nodes:
            yield position

    def add_node(self, node: GraphNode):
        """Add an existing GraphNode to the graph."""
        self.network.add_node(node.position, name=node.name, position=node.position, measure_to=node.measure_to, rotation=node.rotation)

    def add_new_node(self, name: GateName, position: Position, measure_to: int = None, rotation: float = None):
        """Add a new node to the graph."""
        self.network.add_node(position, name=name, position=position, measure_to=measure_to, rotation=rotation)

    def remove_node(self, position: Position):
        self.network.remove_node(position)

    def __getitem__(self, position: Position) -> GraphNode | None:
        """Get the GraphNode at the specified (row, column) Position."""
        if not self.network.has_node(position):
            return None

        node = self.network.nodes[position]
        return GraphNode(node["name"], node["position"], measure_to=node["measure_to"], rotation=node["rotation"])

    def __iter__(self) -> Iterator[GraphNode]:
        """Iterate over the nodes in the graph."""
        for _, data in self.network.nodes(data=True):
            yield GraphNode(data["name"], data["position"], measure_to=data["measure_to"], rotation=data["rotation"])

    def nodes(self) -> list[GraphNode]:
        """Retrieve all the nodes in the graph."""
        return [node for node in self]

    def add_edge(self, edge: GraphEdge):
        """Add an existing GraphEdge to the graph."""
        self.network.add_edge(edge.start.position, edge.end.position, name=edge.name)

    def add_new_edge(self, name: EdgeName, start: Position, end: Position):
        """Add a new edge to the graph."""
        self.network.add_edge(start, end, name=name)

    def iter_edges(self) -> Iterator[GraphEdge]:
        """Iterate over the edges in the graph."""
        for start, end, data in self.network.edges(data=True):
            yield GraphEdge(data["name"], self[start], self[end])

    def edges(self) -> list[GraphEdge]:
        """Retrieve all the edges in the graph."""
        return [edge for edge in self.iter_edges()]

    def iter_node_edges(self, row: int, column: int) -> Iterator[GraphEdge]:
        start = (row, column)

        for _, end, data in self.network.out_edges(start, data=True):
            yield GraphEdge(data["name"], self[start], self[end])

    def node_edges(self, row: int, column: int) -> list[GraphEdge]:
        return [edge for edge in self.iter_node_edges(row, column)]

    def node_edge_data(self, row: int, column: int) -> EdgeData | None:
        start = (row, column)
        origin = self[start]

        if origin is None:
            return None

        edge_data = {
            self._TARGETS.value: [],
            self._CONTROLLED_BY.value: [],
            self._WORKS_WITH.value: []
        }

        for _, end, data in self.network.out_edges(start, data=True):
            edge_name = data["name"]
            destination_node = self[end]

            if edge_name in [self._TARGETS, self._CONTROLLED_BY, self._WORKS_WITH]:
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
        return node.position in self.network

    def __eq__(self, other) -> bool:
        if not isinstance(other, QuantumGraph):
            return NotImplemented

        return networkx.utils.graphs_equal(self.network, other.network)

    def is_occupied(self, row: int, column: int) -> bool:
        """Check whether the graph has a non-filler node at the specified row and column."""
        return self.has_node_at(row, column) and self[row, column].name != GateName.ID

    def has_node_at(self, row: int, column: int) -> bool:
        """Check whether the graph has a node at the specified row and column."""
        return self.network.has_node((row, column))

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
            EdgeName.UP: (row_index - 1, column_index),
            EdgeName.DOWN: (row_index + 1, column_index),
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
        self.network.clear()

    def clear_edges(self):
        """Remove all the edges from the graph."""
        self.network.clear_edges()

    def __len__(self):
        """Get the total number of nodes in the graph."""
        return len(self.network.nodes)

    def copy(self) -> QuantumGraph:
        copy = QuantumGraph()
        copy.network = self.network.copy()
        return copy


@dataclass
class QuantumMetrics:
    """
       Represents quality metrics for a quantum circuit, providing insights into its structure and gate usage.

       Attributes:
           width (int): Number of qubits in the circuit.
           depth (int): Maximum number of operations applied to a qubit in the circuit.

           max_density (int): Maximum number of operations applied to the qubits.
           average_density (float): Average number of operations applied to the qubits.

           pauli_x_count (int): Number of Pauli-X gates (NOT).
           pauli_y_count (int): Number of Pauli-Y gates.
           pauli_z_count (int): Number of Pauli-Z gates.
           pauli_count (int): Total number of Pauli gates in the circuit (calculated as the sum of Pauli-X, Pauli-Y, and Pauli-Z gates).
           hadamard_count (int): Number of Hadamard gates.
           initial_superposition_rate (float): Ratio of qubits with a Hadamard gate as an initial gate (qubits in superposition state).
           other_single_gates_count (int): Number of other single-qubit gates in the circuit (excluding Pauli-X, Pauli-Y, Pauli-Z and Hadamard gates).
           single_gate_count (int): Total number of single-qubit gates.
           controlled_single_qubit_count (int): Total number of controlled single-qubit gates.

           gate_count (int): Total number of gates in the circuit.
           controlled_gate_count (int): Total number of controlled gates in the circuit.
           single_gate_rate (float): Ratio of single gates to total gates.
    """
    # Circuit Size
    width: int = -1
    depth: int = -1

    # Circuit Density
    max_density: int = -1
    average_density: float = -1.0

    # Single-Qubit Gates
    pauli_x_count: int = -1
    pauli_y_count: int = -1
    pauli_z_count: int = -1
    pauli_count: int = -1
    hadamard_count: int = -1
    initial_superposition_rate: float = -1.0
    other_single_gates_count: int = -1
    single_gate_count: int = -1
    controlled_single_qubit_count: int = -1

    # All Gates in the Circuit
    gate_count: int = -1
    controlled_gate_count: int = -1
    single_gate_rate: float = -1.0

    def __str__(self):
        return textwrap.dedent(
            f"""
            Circuit Size:
            - Width: {self.width}
            - Depth: {self.depth}
        
            Circuit Density:
            - Max Density: {self.max_density}
            - Average Density: {self.average_density:.2f}
        
            Single-Qubit Gates:
            - Pauli-X Count: {self.pauli_x_count}
            - Pauli-Y Count: {self.pauli_y_count}
            - Pauli-Z Count: {self.pauli_z_count}
            - Total Pauli Count: {self.pauli_count}
            - Hadamard Count: {self.hadamard_count}
            - Initial Superposition Rate: {self.initial_superposition_rate:.2f}
            - Other Single-Qubit Gates Count: {self.other_single_gates_count}
            - Total Single-Qubit Gates: {self.single_gate_count}
            - Controlled Single-Qubit Gates: {self.controlled_single_qubit_count}
        
            All Gates in the Circuit:
            - Total Gate Count: {self.gate_count}
            - Controlled Gate Count: {self.controlled_gate_count}
            - Single Gate Rate: {self.single_gate_rate:.2f}
            """
        ).strip()
