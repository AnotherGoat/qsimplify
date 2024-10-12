from __future__ import annotations
from dataclasses import dataclass
from typing import TypeAlias, List
from networkx.classes import MultiDiGraph
from quantum_circuit_simplifier.utils import setup_logger

class GridNode:
    """
    Represents a node of a QuantumGrid.

    Attributes:
        name (str): The name of quantum gate represented by this node.
        targets (list[int]): A list of target node indices that this .
        controlled_by (list[int]): A list of node indices that control this node.
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
        target_data = f"targets={self.targets}" if self.targets else ""
        controlled_by_data = f"controlled_by={self.controlled_by}" if self.controlled_by else ""
        extra_data = [data for data in [target_data, controlled_by_data] if data]

        if len(extra_data) == 0:
            return self.name

        return f"{self.name}({', '.join(extra_data)})"


GridData: TypeAlias = List[List[GridNode]]
"""Represents a 2D list of GridNodes, which is commonly used by a QuantumGrid to hold its data."""

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

    def __getitem__(self, index: tuple[int, int]) -> GridNode:
        """Get the node at the specified (row, column) index."""
        row, column = index
        return self._data[row][column]

    def __setitem__(self, index: tuple[int, int], value: GridNode):
        """Set the node at the specified (row, column) index."""
        row, column = index
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


class QuantumGraph(MultiDiGraph):
    """
    Represents a QuantumCircuit as a NetworkX Graph.
    """


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
