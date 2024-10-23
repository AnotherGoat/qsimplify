import textwrap
from dataclasses import dataclass


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
