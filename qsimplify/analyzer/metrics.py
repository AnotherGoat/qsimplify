import textwrap
from dataclasses import dataclass


@dataclass(frozen=True)
class Metrics:
    """Defines a set of metrics that can be used to estimate the complexity and quality of a quantum circuit.

    Attributes:
        qubit_count: Number of qubits in the circuit.
        depth: Maximum number of operations applied to a qubit in the circuit.
        x_count: Number of Pauli X (NOT) gates.
        y_count: Number of Pauli Y gates.
        z_count: Number of Pauli Z gates.
        pauli_count: Total number of Pauli X (NOT), Y and Z gates.
        hadamard_count: Number of Hadamard gates.
        rotation_count: Number of rotation gates.
        square_root_count: Number of square root gates.
        measure_count: Number of measured qubits.
        swap_count: Number of SWAP gates.
        cx_count: Number of CX (CNOT) gates.
        gate_count: Total number of gates.
        single_gate_count: Total number of single-qubit gates.
        controlled_gate_count: Total number of controlled gates.
        ancilla_qubit_count: Number of ancilla qubits (qubits that are not measured).
        gate_types_count: Number of different gates used in the circuit.

    """

    qubit_count: int
    depth: int
    x_count: int
    y_count: int
    z_count: int
    pauli_count: int
    hadamard_count: int
    rotation_count: int
    square_root_count: int
    measure_count: int
    swap_count: int
    cx_count: int
    gate_count: int
    single_gate_count: int
    controlled_gate_count: int
    ancilla_qubit_count: int
    gate_types_count: int


@dataclass(frozen=True)
class DeltaMetrics:
    """Defines the difference in metrics between two quantum circuits.

    Attributes:
        qubit_count: Difference in qubits in the circuit.
        depth: Difference in maximum number of operations applied to a qubit in the circuit.
        x_count: Difference in Pauli X (NOT) gates.
        y_count: Difference in Pauli Y gates.
        z_count: Difference in Pauli Z gates.
        pauli_count: Difference in total of Pauli X (NOT), Y and Z gates.
        hadamard_count: Difference in Hadamard gates.
        rotation_count: Difference in rotation gates.
        square_root_count: Difference in square root gates.
        measure_count: Difference in measured qubits.
        swap_count: Difference in SWAP gates.
        cx_count: Difference in CX (CNOT) gates.
        gate_count: Difference in total number of gates.
        single_gate_count: Difference in single-qubit gates.
        controlled_gate_count: Difference in controlled gates.
        ancilla_qubit_count: Difference in ancilla qubits (qubits that are not measured).
        gate_types_count: Difference in different gates used in the circuit.

    """

    qubit_count: int | None = None
    depth: int | None = None
    x_count: int | None = None
    y_count: int | None = None
    z_count: int | None = None
    pauli_count: int | None = None
    hadamard_count: int | None = None
    rotation_count: int | None = None
    square_root_count: int | None = None
    measure_count: int | None = None
    swap_count: int | None = None
    cx_count: int | None = None
    gate_count: int | None = None
    single_gate_count: int | None = None
    controlled_gate_count: int | None = None
    ancilla_qubit_count: int | None = None
    gate_types_count: int | None = None


@dataclass(frozen=True)
class DetailedMetrics:
    """Represents quality metrics for a quantum circuit, providing insights into its structure and gate usage.

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
