from qiskit import QuantumCircuit

from qsimplify.analyzer.quantum_metrics import QuantumMetrics
from qsimplify.converter import Converter
from qsimplify.model import GateName, Position, QuantumGraph


class Analyzer:
    def __init__(self, converter: Converter) -> None:
        self._converter = converter

    def calculate_metrics(self, circuit: QuantumCircuit) -> QuantumMetrics:
        graph = self._converter.circuit_to_graph(circuit)
        gate_count = len(circuit.data)
        x_count = self._count_operations(circuit, GateName.X)
        y_count = self._count_operations(circuit, GateName.Y)
        z_count = self._count_operations(circuit, GateName.Z)
        pauli_count = x_count + y_count + z_count
        hadamard_count = self._count_operations(circuit, GateName.H)
        single_gate_count = self._count_single_gates(circuit)

        return QuantumMetrics(
            width=graph.height,
            depth=graph.width,
            max_density=graph.width,
            gate_count=gate_count,
            pauli_x_count=x_count,
            pauli_y_count=y_count,
            pauli_z_count=z_count,
            pauli_count=pauli_count,
            hadamard_count=hadamard_count,
            initial_superposition_percent=self._calculate_superposition_rate(graph),
            single_gate_count=self._count_single_gates(circuit),
            other_single_gates_count=single_gate_count - pauli_count - hadamard_count,
            single_gate_percent=single_gate_count / gate_count,
        )

    def _count_operations(self, circuit: QuantumCircuit, gate_name: GateName) -> int:
        operations = self._get_operations(circuit)
        return len([operation for operation in operations if operation == gate_name.value])

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
