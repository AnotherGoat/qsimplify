from qiskit import QuantumCircuit
from quantum_circuit_simplifier.converter import circuit_to_grid, get_qubit_indexes
from quantum_circuit_simplifier.model import QuantumMetrics, QuantumGrid


def get_operations(circuit: QuantumCircuit) -> list[str]:
    return [instruction.operation.name for instruction in circuit.data]


def count_operations(circuit: QuantumCircuit, operation_name: str) -> int:
    operations = get_operations(circuit)
    return len([operation for operation in operations if operation == operation_name])


def calculate_superposition_rate(grid: QuantumGrid) -> float:
    superposition_count = 0

    for row in grid.data:
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
    metrics.width = grid.height
    metrics.depth = grid.width

    metrics.max_density = grid.width

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
