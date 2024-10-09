from dataclasses import dataclass
from qiskit import QuantumCircuit
from quantum_circuit_simplifier.converter import circuit_to_grid, GridNode, get_qubit_indexes


@dataclass
class QuantumMetrics:
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


def get_operations(circuit: QuantumCircuit) -> list[str]:
    return [instruction.operation.name for instruction in circuit.data]


def count_operations(circuit: QuantumCircuit, operation_name: str) -> int:
    operations = get_operations(circuit)
    return len([operation for operation in operations if operation == operation_name])


def calculate_superposition_rate(grid: list[list[GridNode]]) -> float:
    superposition_count = 0

    for row in grid:
        for grid_node in row:
            if grid_node.name == "i":
                continue

            if grid_node.name == "h":
                superposition_count += 1

            break

    return superposition_count / len(grid)


def count_single_qubit_gates(circuit: QuantumCircuit) -> int:
    qubit_counts = [len(get_qubit_indexes(circuit, instruction)) for instruction in circuit.data ]
    return len([qubit_count for qubit_count in qubit_counts if qubit_count == 1])


def analyze(circuit: QuantumCircuit) -> QuantumMetrics:
    metrics = QuantumMetrics()

    grid = circuit_to_grid(circuit)
    metrics.width = len(grid)
    metrics.depth = len(grid[0])

    metrics.max_density = len(grid[0])

    metrics.gate_count = len(circuit.data)

    metrics.pauli_x_count = count_operations(circuit, "x")
    metrics.pauli_y_count = count_operations(circuit, "y")
    metrics.pauli_z_count = count_operations(circuit, "z")
    metrics.pauli_count = metrics.pauli_x_count + metrics.pauli_y_count + metrics.pauli_z_count
    metrics.hadamard_count = count_operations(circuit, "h")
    metrics.initial_superposition_rate = calculate_superposition_rate(grid)
    metrics.single_gate_count = count_single_qubit_gates(circuit)
    metrics.other_single_gates_count = metrics.single_gate_count - metrics.pauli_count - metrics.hadamard_count

    metrics.single_gate_rate = metrics.single_gate_count / metrics.gate_count

    return metrics
