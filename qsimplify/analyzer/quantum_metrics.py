import textwrap
from dataclasses import dataclass


@dataclass(frozen=True)
class QuantumMetrics:
    """
    Represents quality metrics for a quantum circuit, providing insights into its structure and gate usage.

    Attributes:
        width (int): Number of qubits in the circuit.
        depth (int): Maximum number of operations applied to a qubit in the circuit.

        max_density (int): Maximum number of operations applied to the qubits.
        average_density (float): Average number of operations applied to the qubits.

        x_count (int): Number of Pauli-X gates (NOT).
        y_count (int): Number of Pauli-Y gates.
        z_count (int): Number of Pauli-Z gates.
        pauli_count (int): Total number of Pauli gates in the circuit (calculated as the sum of Pauli-X, Pauli-Y, and Pauli-Z gates).
        hadamard_count (int): Number of Hadamard gates.
        initial_superposition_percent (float): Ratio of qubits with a Hadamard gate as an initial gate (qubits in superposition state).
        other_single_qubit_count (int): Number of other single-qubit gates in the circuit (excluding Pauli-X, Pauli-Y, Pauli-Z and Hadamard gates).
        single_qubit_count (int): Total number of single-qubit gates.
        single_controlled_qubit_count (int): Total number of controlled single-qubit gates.

        gate_count (int): Total number of gates in the circuit.
        controlled_gate_count (int): Total number of controlled gates in the circuit.
        single_qubit_percent (float): Ratio of single gates to total gates.
    """

    # Circuit Size
    width: int
    depth: int

    # Circuit Density
    max_density: int
    average_density: float

    # Single-Qubit Gates
    x_count: int
    y_count: int
    z_count: int
    pauli_count: int
    hadamard_count: int
    initial_superposition_percent: float
    other_single_qubit_count: int
    single_qubit_count: int
    single_controlled_qubit_count: int

    # Multi-Qubit Gates
    swap_count: int
    cnot_count: int
    cnot_qubit_percent: float
    average_cnot: float
    max_cnot: int
    toffoli_count: int
    toffoli_qubit_percent: float
    average_toffoli: float
    max_toffoli: int

    # All Gates in the Circuit
    gate_count: int
    controlled_gate_count: int
    single_qubit_percent: float

    # Measurement Gates
    measure_count: int
    measure_percent: float

    # Other Metrics
    ancilla_percent: float

    def __str__(self) -> str:
        return textwrap.dedent(
            f"""
            Circuit Size:
            - Width: {self.width}
            - Depth: {self.depth}

            Circuit Density:
            - MaxDens (Max Density): {self.max_density}
            - AvgDens (Average Density): {self.average_density:.2f}

            Single-Qubit Gates:
            - NoP-X (Pauli-X Count): {self.x_count}
            - NoP-Y (Pauli-Y Count): {self.y_count}
            - NoP-Z (Pauli-Z Count): {self.z_count}
            - TNo-P (Total Pauli Count): {self.pauli_count}
            - NoH (Hadamard Count): {self.hadamard_count}
            - %SpposQ (Initial Superposition Percent): {self.initial_superposition_percent:.2f}
            - NoOtherSG (Other Single-Qubit Gates Count): {self.other_single_qubit_count}
            - TNoSQG (Total Single-Qubit Gates): {self.single_qubit_count}
            - TNoSQG (Controlled Single-Qubit Gates): {self.single_controlled_qubit_count}

            Multi-Qubit Gates:
            - NoSWAP (SWAP Count): {self.swap_count}
            - NoCNOT (CNOT Count): {self.cnot_count}
            - %QinCNOT (Ratio of qubits affected by CNOT Gates): {self.cnot_qubit_percent:.2f}
            - AvgCNOT (Average CNOT Gates): {self.average_cnot}
            - MaxCNOT (Max CNOT Gates): {self.max_cnot}
            - NoToff (Toffoli Count): {self.toffoli_count}
            - %QinToff (Ratio of qubits affected by Toffoli Gates): {self.toffoli_qubit_percent:.2f}
            - AvgToff (Average Toffoli Gates): {self.average_toffoli}
            - MaxToff (Max Toffoli Gates): {self.max_toffoli}

            All Gates in the Circuit:
            - NoGates (Total Gate Count): {self.gate_count}
            - NoCAnyG/NoCGates (Controlled Gate Count): {self.controlled_gate_count}
            - %SGates (Single Gate Percent): {self.single_qubit_percent:.2f}
            
            Measurement Gates:
            - NoQM (Measured Qubit Count): {self.measure_count}
            - %QM (Measured Qubit Percent): {self.measure_percent:.2f}
            
            Other Measurements:
            - %Anc (Ancilla Qubit Percent): {self.ancilla_percent:.2f}
            """
        ).strip()
