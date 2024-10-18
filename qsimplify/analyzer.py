from qiskit import QuantumCircuit
from qsimplify.converter import Converter
from qsimplify.model import QuantumMetrics, GateName, QuantumGraph


def _get_operations(circuit: QuantumCircuit) -> list[str]:
    return [instruction.operation.name for instruction in circuit.data]


def _count_operations(circuit: QuantumCircuit, operation_name: str) -> int:
    operations = _get_operations(circuit)
    return len([operation for operation in operations if operation == operation_name])


def _calculate_superposition_rate(graph: QuantumGraph) -> float:
    superposition_count = 0
    row = 0

    while graph.has_node_at(row, 0):
        node = graph[row, 0]

        if node.name == GateName.H:
            superposition_count += 1

        row += 1

    return superposition_count / graph.height


def _count_single_qubit_gates(circuit: QuantumCircuit) -> int:
    qubit_counts = [instruction.operation.num_qubits for instruction in circuit.data ]
    return len([qubit_count for qubit_count in qubit_counts if qubit_count == 1])


def analyze(circuit: QuantumCircuit, converter: Converter) -> QuantumMetrics:
    metrics = QuantumMetrics()

    graph = converter.circuit_to_graph(circuit)
    metrics.width = graph.height
    metrics.depth = graph.width

    metrics.max_density = graph.width

    metrics.gate_count = len(circuit.data)

    metrics.pauli_x_count = _count_operations(circuit, GateName.X.value)
    metrics.pauli_y_count = _count_operations(circuit, GateName.Y.value)
    metrics.pauli_z_count = _count_operations(circuit, GateName.Z.value)
    metrics.pauli_count = metrics.pauli_x_count + metrics.pauli_y_count + metrics.pauli_z_count
    metrics.hadamard_count = _count_operations(circuit, GateName.H.value)
    metrics.initial_superposition_rate = _calculate_superposition_rate(graph)
    metrics.single_gate_count = _count_single_qubit_gates(circuit)
    metrics.other_single_gates_count = metrics.single_gate_count - metrics.pauli_count - metrics.hadamard_count

    metrics.single_gate_rate = metrics.single_gate_count / metrics.gate_count

    return metrics
