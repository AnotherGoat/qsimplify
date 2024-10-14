from __future__ import annotations
from dataclasses import dataclass
from typing import TypeAlias, List, Any, Tuple
from networkx.classes import MultiDiGraph
import textwrap

class GridNode:
    """
    Represents a node of a QuantumGrid.

    Attributes:
        name (str): The name of quantum gate represented by this node.
        targets (list[int]): A list of target node rows.
        controlled_by (list[int]): A list of node rows that control this node.
    """

    def __init__(self, name: str, targets: list[int] = None, controlled_by: list[int] = None):
        self.name = name
        self.targets: list[int] = [] if targets is None else targets
        self.controlled_by: list[int] = [] if controlled_by is None else controlled_by

    def __eq__(self, other) -> bool:
        if not isinstance(other, GridNode):
            return NotImplemented

        return self.name == other.name and self.targets == other.targets and self.controlled_by == other.controlled_by

    def __str__(self) -> str:
        extra_data = [
            f"targets={self.targets}" if self.targets else "",
            f"controlled_by={self.controlled_by}" if self.controlled_by else ""
        ]
        extra_data = [data for data in extra_data if data]

        if len(extra_data) == 0:
            return self.name

        return f"{self.name}({', '.join(extra_data)})"


GridData: TypeAlias = List[List[GridNode]]
"""Represents a 2D list of GridNodes, which is commonly used by a QuantumGrid to hold its data."""

Position: TypeAlias = Tuple[int, int]
"""Represents a (row, column) position in a QuantumGrid."""

class QuantumGrid:
    """
    Represents a QuantumCircuit as a 2D list of GridNodes.

    Each qubit is represented by a row in the grid.
    Single-qubit gates occupy a single GridNode, while multi-qubit gates use multiple related GridNodes (one for each qubit involved).
    Empty slots are represented by the FILLER node.

    Attributes:
        FILLER (GridNode): The default node used to represent empty slots in the grid.
        width (int): The number of columns in the grid.
        height (int): The number of rows (qubits) in the grid.
    """
    FILLER = GridNode("id")
    width: int
    height: int
    _data: GridData

    @property
    def data(self) -> GridData:
        """A 2D list representing the grid data, where each element is a GridNode."""
        return self._data

    @data.setter
    def data(self, value: GridData):
        self._data = value
        self.height = len(self.data)
        self.width = len(self.data[0])

    @staticmethod
    def create_empty(width: int, height: int) -> QuantumGrid:
        """Create an empty QuantumGrid of the specified width and height."""
        return QuantumGrid([[QuantumGrid.FILLER for _ in range(width)] for _ in range(height)])

    def __init__(self, data: GridData):
        """Create a QuantumGrid by providing a 2D list."""
        self.data = data

    def trim_right_side(self) -> QuantumGrid:
        """Create a copy of this grid with the filler on the right side removed."""
        columns_to_trim = 0

        for column in range(self.width - 1, -1, -1):
            if all(row[column] == QuantumGrid.FILLER for row in self.data):
                columns_to_trim += 1
            else:
                break

        return QuantumGrid([row[0:self.width - columns_to_trim] for row in self.data])

    def __str__(self) -> str:
        columns = zip(*self.data)
        column_lengths = []

        for column in columns:
            max_text_length = max(len(str(node)) for node in column)
            column_lengths.append(max_text_length)

        rows = []

        for row_index, row in enumerate(self.data):
            formatted_values = [
                f"{str(value):<{max_text_length}}"
                for value, max_text_length in zip(row, column_lengths)
            ]

            row_data = "    ".join(formatted_values)
            rows.append(f"{row_index}: {row_data}")

        return "\n".join(rows)

    def is_occupied(self, row: int, column: int) -> bool:
        return self[row, column] != QuantumGrid.FILLER

    def has_node_at(self, row: int, column: int) -> bool:
        """Check whether the grid has a node at the specified row and column."""
        return 0 <= row < self.height and 0 <= column < self.width

    def __getitem__(self, position: Position) -> GridNode:
        """Get the node at the specified (row, column) position."""
        row, column = position
        return self._data[row][column]

    def __setitem__(self, position: Position, value: GridNode):
        """Set the node at the specified (row, column) position."""
        row, column = position
        self._data[row][column] = value

    def __iter__(self):
        """Iterate over the grid node by node."""
        for row in self.data:
            for node in row:
                yield node

    def __len__(self):
        """Get the total number of nodes in the grid."""
        return self.height * self.width

    def iter_rows(self):
        """Iterate over the grid row by row."""
        for row in self._data:
            yield row

    def iter_columns(self):
        """Iterate over the grid column by column."""
        for col in range(self.width):
            yield [self._data[row][col] for row in range(self.height)]


class GraphNode:
    def __init__(self, name: str, position: Position | None = None):
        self.name = name
        self.position = position

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this class' attributes."""
        return {"name": self.name, "position": self.position}

    def __eq__(self, other) -> bool:
        if not isinstance(other, GraphNode):
            return NotImplemented

        return self.name == other.name and self.position == other.position

    def __str__(self):
        return f"{self.name} at {self.position}"


class GraphEdge:
    def __init__(self, name: str, start: GraphNode, end: GraphNode):
        self.name = name
        self.start = start
        self.end = end

    def __str__(self):
        return f"[{self.name}] from {self.start} to {self.end}"


class EdgeData:
    def __init__(
        self,
        origin: GraphNode,
        up: GraphNode = None,
        down: GraphNode = None,
        left: GraphNode = None,
        right: GraphNode = None,
        targets: list[GraphNode] = None,
        controlled_by: list[GraphNode] = None
    ):
        self.origin = origin
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        self.targets = targets if targets is not None else []
        self.controlled_by = controlled_by if controlled_by is not None else []

    def __str__(self) -> str:
        target_names = [str(target) for target in self.targets]
        controller_names = [str(controller) for controller in self.controlled_by]
        extra_data = [
            f"up={self.up}" if self.up else "",
            f"down={self.down}" if self.down else "",
            f"left={self.left}" if self.left else "",
            f"right={self.right}" if self.right else "",
            f"targets={target_names}" if target_names else "",
            f"controlled_by={controller_names}" if controller_names else ""
        ]
        extra_data = [data for data in extra_data if data]

        if len(extra_data) == 0:
            return str(self.origin)

        return f"{self.origin}({', '.join(extra_data)})"


class QuantumGraph:
    """
    Represents a QuantumCircuit as a NetworkX Graph.
    Tuples of the form (row, column) are used to index the graph's nodes.
    """
    def __init__(self):
        self.network = MultiDiGraph()

    @property
    def width(self) -> int:
        return max(position[1] for position in self.get_positions()) + 1

    @property
    def height(self) -> int:
        return max(position[0] for position in self.get_positions()) + 1

    def get_positions(self) -> list[Position]:
        return [position for position in self.network.nodes]

    def add_gate_node(self, position: Position, node: GraphNode):
        self.network.add_node(position, **node.to_dict())

    def __getitem__(self, position: Position) -> GraphNode:
        """Get the node at the specified (row, column) position."""
        node = self.network.nodes[position]
        return GraphNode(node["name"], node["position"])

    def get_gate_nodes(self) -> list[GraphNode]:
        return [GraphNode(node[1]["name"], node[1]["position"]) for node in self.network.nodes(data=True)]

    def add_edge(self, name: str, start: Position, end: Position):
        self.network.add_edge(start, end, name=name)

    def get_edges(self) -> list[GraphEdge]:
        return [GraphEdge(data["name"], self[start], self[end]) for start, end, data in self.network.edges(data=True)]

    def find_edges(self, row: int, column: int) -> EdgeData:
        position = (row, column)
        origin = self[position]
        edges = self.network.out_edges(position, data=True)
        edge_data = {
            "targets": [],
            "controlled_by": []
        }

        for _, destination, data in edges:
            edge_name = data["name"]
            destination_node = self[destination]

            if edge_name == "targets":
                edge_data["targets"].append(destination_node)
            elif edge_name == "controlled_by":
                edge_data["controlled_by"].append(destination_node)
            else:
                edge_data[edge_name] = destination_node

        return EdgeData(origin, **edge_data)

    def __str__(self):
        result = ["Nodes:"]
        result += [str(node) for node in self.get_gate_nodes()]
        result += ["\nEdges:"]
        result += [str(edge) for edge in self.get_edges()]
        return "\n".join(result)

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
