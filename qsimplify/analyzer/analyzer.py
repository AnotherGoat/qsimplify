from typing import Iterable

from qsimplify.analyzer.quantum_metrics import QuantumMetrics
from qsimplify.converter import Converter
from qsimplify.model import GateName, Position, QuantumGraph, GraphNode, EdgeName

_SINGLE_QUBIT_GATES = {gate_name for gate_name in GateName if gate_name.number_of_qubits() == 1}
_SINGLE_CONTROLLED_GATES = {gate_name for gate_name in GateName if gate_name.is_single_controlled()}
_CONTROLLED_GATES = {gate_name for gate_name in GateName if gate_name.is_controlled()}

class Analyzer:
    def __init__(self, converter: Converter) -> None:
        self._converter = converter

    def calculate_metrics(self, graph: QuantumGraph) -> QuantumMetrics:
        gate_count = self._count_total_gates(graph)
        x_count = self._count_gates(graph, GateName.X)
        y_count = self._count_gates(graph, GateName.Y)
        z_count = self._count_gates(graph, GateName.Z)
        pauli_count = x_count + y_count + z_count
        hadamard_count = self._count_gates(graph, GateName.H)
        single_gate_count = self._count_single_gates(graph)
        cnot_count = self._count_gates(graph, GateName.CX)
        toffoli_count = self._count_gates(graph, GateName.CCX)
        single_qubit_percent = 0 if gate_count == 0 else single_gate_count / gate_count
        measure_count = self._count_measured_qubits(graph)
        measure_percent = 0 if len(graph) == 0 else measure_count / graph.height

        return QuantumMetrics(
            width=graph.height,
            depth=graph.width,
            max_density=self._calculate_max_density(graph),
            average_density=self._calculate_average_density(graph),
            x_count=x_count,
            y_count=y_count,
            z_count=z_count,
            pauli_count=pauli_count,
            hadamard_count=hadamard_count,
            initial_superposition_percent=self._calculate_superposition_percent(graph),
            single_qubit_count=self._count_single_gates(graph),
            other_single_qubit_count=single_gate_count - pauli_count - hadamard_count,
            single_controlled_qubit_count=self._count_single_controlled_gates(graph),
            swap_count=self._count_gates(graph, GateName.SWAP),
            cnot_count=cnot_count,
            cnot_qubit_percent=self._calculate_cnot_qubit_percent(graph),
            average_cnot=0 if len(graph) == 0 else cnot_count / graph.height,
            max_cnot=self._count_max_cnot(graph),
            toffoli_count=toffoli_count,
            toffoli_qubit_percent=self._calculate_toffoli_qubit_percent(graph),
            average_toffoli=0 if len(graph) == 0 else toffoli_count / graph.height,
            max_toffoli=self._count_max_toffoli(graph),
            gate_count=gate_count,
            controlled_gate_count=self._count_controlled_gates(graph),
            single_qubit_percent=single_qubit_percent,
            measure_count=measure_count,
            measure_percent=measure_percent,
            ancilla_percent=1 - measure_percent
        )

    @staticmethod
    def _count_total_gates(graph: QuantumGraph) -> int:
        if len(graph) == 0:
            return 0

        return sum(Analyzer._count_gates(graph, gate_name) for gate_name in GateName)

    @staticmethod
    def _count_gates(nodes: Iterable[GraphNode], gate_name: GateName) -> int:
        if gate_name.number_of_qubits() == 0:
            return 0

        return len([node for node in nodes if node.name == gate_name]) // gate_name.number_of_qubits()

    @staticmethod
    def _calculate_superposition_percent(graph: QuantumGraph) -> float:
        if len(graph) == 0:
            return 0

        first_column = Analyzer._get_column(graph, 0)
        hadamard_count = Analyzer._count_gates(first_column, GateName.H)

        return hadamard_count / graph.height

    @staticmethod
    def _count_single_gates(graph: QuantumGraph) -> int:
        return sum([Analyzer._count_gates(graph, gate_name) for gate_name in _SINGLE_QUBIT_GATES])

    @staticmethod
    def _calculate_max_density(graph: QuantumGraph) -> int:
        max_density = 0

        for column_index in range(graph.width):
            density = Analyzer._calculate_column_density(graph, column_index)
            max_density = max(max_density, density)

        return max_density

    @staticmethod
    def _calculate_column_density(graph: QuantumGraph, column_index: int) -> int:
        column = Analyzer._get_column(graph, column_index)
        gate_names = {node.name for node in column}
        return sum([Analyzer._count_gates(column, gate_name) for gate_name in gate_names])

    @staticmethod
    def _get_column(graph: QuantumGraph, column_index: int) -> list[GraphNode]:
        column = []

        for row_index in range(graph.height):
            position = Position(row_index, column_index)

            if not graph.has_node_at(position):
                continue

            column.append(graph[position])

        return column

    @staticmethod
    def _calculate_average_density(graph: QuantumGraph) -> float:
        if len(graph) == 0:
            return 0

        densities = [Analyzer._calculate_column_density(graph, column) for column in range(graph.width)]
        return sum(densities) / len(densities)

    @staticmethod
    def _count_single_controlled_gates(graph: QuantumGraph) -> int:
        return sum([Analyzer._count_gates(graph, gate_name) for gate_name in _SINGLE_CONTROLLED_GATES])

    @staticmethod
    def _count_controlled_gates(graph: QuantumGraph) -> int:
        return sum([Analyzer._count_gates(graph, gate_name) for gate_name in _CONTROLLED_GATES])

    @staticmethod
    def _calculate_cnot_qubit_percent(graph: QuantumGraph) -> float:
        if len(graph) == 0:
            return 0

        rows_with_cnot = {node.position.row for node in graph if node.name == GateName.CX}
        return len(rows_with_cnot) / graph.height

    @staticmethod
    def _count_max_cnot(graph: QuantumGraph) -> int:
        if len(graph) == 0:
            return 0

        counts: dict[int, int] = {}

        for node in graph:
            if node.name != GateName.CX:
                continue

            position = node.position
            edges = graph.node_edges(position)

            if not any(edge.name == EdgeName.CONTROLLED_BY for edge in edges):
                continue

            if position.row in counts:
                counts[position.row] += 1
            else:
                counts[position.row] = 1

        if len(counts) == 0:
            return 0

        return max(counts.values())

    @staticmethod
    def _calculate_toffoli_qubit_percent(graph: QuantumGraph) -> float:
        if len(graph) == 0:
            return 0

        rows_with_toffoli = {node.position.row for node in graph if node.name == GateName.CCX}
        return len(rows_with_toffoli) / graph.height

    @staticmethod
    def _count_max_toffoli(graph: QuantumGraph) -> int:
        if len(graph) == 0:
            return 0

        counts: dict[int, int] = {}

        for node in graph:
            if node.name != GateName.CCX:
                continue

            position = node.position
            edges = graph.node_edges(position)

            if not any(edge.name == EdgeName.CONTROLLED_BY for edge in edges):
                continue

            if position.row in counts:
                counts[position.row] += 1
            else:
                counts[position.row] = 1

        if len(counts) == 0:
            return 0

        return max(counts.values())

    @staticmethod
    def _count_measured_qubits(graph: QuantumGraph) -> int:
        if len(graph) == 0:
            return 0

        measured_rows = {node.position.row for node in graph if node.name == GateName.MEASURE}
        return len(measured_rows)
