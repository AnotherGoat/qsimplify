from qiskit import QuantumCircuit
from quantum_circuit_simplifier.converter import Converter
from quantum_circuit_simplifier.model import QuantumMetrics, QuantumGrid, GateName


def _get_operations(circuit: QuantumCircuit) -> list[str]:
    return [instruction.operation.name for instruction in circuit.data]


def _count_operations(circuit: QuantumCircuit, operation_name: str) -> int:
    operations = _get_operations(circuit)
    return len([operation for operation in operations if operation == operation_name])


def _calculate_superposition_rate(grid: QuantumGrid) -> float:
    superposition_count = 0

    for row in grid.data:
        for grid_node in row:
            if grid_node == QuantumGrid.FILLER:
                continue

            if grid_node.name == GateName.H:
                superposition_count += 1

            break

    return superposition_count / len(grid)


def _count_single_qubit_gates(circuit: QuantumCircuit) -> int:
    qubit_counts = [instruction.operation.num_qubits for instruction in circuit.data ]
    return len([qubit_count for qubit_count in qubit_counts if qubit_count == 1])


def analyze(circuit: QuantumCircuit, converter: Converter) -> QuantumMetrics:
    metrics = QuantumMetrics()

    grid = converter.circuit_to_grid(circuit)
    metrics.width = grid.height
    metrics.depth = grid.width

    metrics.max_density = grid.width

    metrics.gate_count = len(circuit.data)

    metrics.pauli_x_count = _count_operations(circuit, GateName.X.value)
    metrics.pauli_y_count = _count_operations(circuit, GateName.Y.value)
    metrics.pauli_z_count = _count_operations(circuit, GateName.Z.value)
    metrics.pauli_count = metrics.pauli_x_count + metrics.pauli_y_count + metrics.pauli_z_count
    metrics.hadamard_count = _count_operations(circuit, GateName.H.value)
    metrics.initial_superposition_rate = _calculate_superposition_rate(grid)
    metrics.single_gate_count = _count_single_qubit_gates(circuit)
    metrics.other_single_gates_count = metrics.single_gate_count - metrics.pauli_count - metrics.hadamard_count

    metrics.single_gate_rate = metrics.single_gate_count / metrics.gate_count

    return metrics
