from qiskit import QuantumCircuit

from qsimplify.analyzer.quantum_metrics import QuantumMetrics
from qsimplify.converter import Converter
from qsimplify.model import GateName, Position, QuantumGraph


class Analyzer:
    def __init__(self, converter: Converter):
        self._converter = converter

    def calculate_metrics(self, circuit: QuantumCircuit) -> QuantumMetrics:
        metrics = QuantumMetrics()

        graph = self._converter.circuit_to_graph(circuit)
        metrics.width = graph.height
        metrics.depth = graph.width

        metrics.max_density = graph.width

        metrics.gate_count = len(circuit.data)

        metrics.pauli_x_count = self._count_operations(circuit, GateName.X.value)
        metrics.pauli_y_count = self._count_operations(circuit, GateName.Y.value)
        metrics.pauli_z_count = self._count_operations(circuit, GateName.Z.value)
        metrics.pauli_count = metrics.pauli_x_count + metrics.pauli_y_count + metrics.pauli_z_count
        metrics.hadamard_count = self._count_operations(circuit, GateName.H.value)
        metrics.initial_superposition_percent = self._calculate_superposition_rate(graph)
        metrics.single_gate_count = self._count_single_gates(circuit)
        metrics.other_single_gates_count = (
            metrics.single_gate_count - metrics.pauli_count - metrics.hadamard_count
        )

        metrics.single_gate_percent = metrics.single_gate_count / metrics.gate_count

        return metrics

    def _count_operations(self, circuit: QuantumCircuit, operation_name: str) -> int:
        operations = self._get_operations(circuit)
        return len([operation for operation in operations if operation == operation_name])

    @staticmethod
    def _get_operations(circuit: QuantumCircuit) -> list[str]:
        return [instruction.operation.name for instruction in circuit.data]

    @staticmethod
    def _calculate_superposition_rate(graph: QuantumGraph) -> float:
        superposition_count = 0
        row = 0
        position = Position(row, 0)

        while graph.has_node_at(position):
            node = graph[position]

            if node.name == GateName.H:
                superposition_count += 1

            row += 1
            position = Position(row, 0)

        return superposition_count / graph.height

    @staticmethod
    def _count_single_gates(circuit: QuantumCircuit) -> int:
        qubit_counts = [instruction.operation.num_qubits for instruction in circuit.data]
        return len([qubit_count for qubit_count in qubit_counts if qubit_count == 1])
