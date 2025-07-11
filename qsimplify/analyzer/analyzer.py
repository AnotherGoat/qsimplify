from dataclasses import fields
from typing import Iterable

from qsimplify.analyzer.metrics import DeltaMetrics, DetailedMetrics, Metrics
from qsimplify.model import EdgeName, GateName, GraphNode, Position, QuantumGraph

_ROTATION_GATES = {gate_name for gate_name in GateName if gate_name.is_rotation()}
_SQUARE_ROOT_GATES = {gate_name for gate_name in GateName if gate_name.is_square_root()}
_SINGLE_QUBIT_GATES = {gate_name for gate_name in GateName if gate_name.number_of_qubits() == 1}
_SINGLE_CONTROLLED_GATES = {gate_name for gate_name in GateName if gate_name.is_single_controlled()}
_CONTROLLED_GATES = {gate_name for gate_name in GateName if gate_name.is_controlled()}


def calculate_metrics(graph: QuantumGraph) -> Metrics:
    qubit_count = graph.height
    x_count = _count_gates(graph, GateName.X)
    y_count = _count_gates(graph, GateName.Y)
    z_count = _count_gates(graph, GateName.Z)
    measure_count = _count_measured_qubits(graph)

    return Metrics(
        qubit_count=qubit_count,
        depth=graph.width,
        x_count=x_count,
        y_count=y_count,
        z_count=z_count,
        pauli_count=x_count + y_count + z_count,
        hadamard_count=_count_gates(graph, GateName.H),
        rotation_count=_count_rotation_gates(graph),
        square_root_count=_count_square_root_gates(graph),
        measure_count=measure_count,
        swap_count=_count_gates(graph, GateName.SWAP),
        cx_count=_count_gates(graph, GateName.CX),
        gate_count=_count_total_gates(graph),
        single_gate_count=_count_single_gates(graph),
        controlled_gate_count=_count_controlled_gates(graph),
        ancilla_qubit_count=qubit_count - measure_count,
        gate_types_count=_count_gate_types(graph),
    )


def compare_metrics(old: QuantumGraph, new: QuantumGraph) -> DeltaMetrics:
    old_metrics = calculate_metrics(old)
    new_metrics = calculate_metrics(new)

    deltas: dict[str, int] = {}

    for field in fields(DeltaMetrics):
        delta = getattr(new_metrics, field.name) - getattr(old_metrics, field.name)

        if delta != 0:
            deltas[field.name] = delta

    return DeltaMetrics(**deltas)


def calculate_detailed_metrics(graph: QuantumGraph) -> DetailedMetrics:
    gate_count = _count_total_gates(graph)
    x_count = _count_gates(graph, GateName.X)
    y_count = _count_gates(graph, GateName.Y)
    z_count = _count_gates(graph, GateName.Z)
    pauli_count = x_count + y_count + z_count
    hadamard_count = _count_gates(graph, GateName.H)
    single_gate_count = _count_single_gates(graph)
    cnot_count = _count_gates(graph, GateName.CX)
    toffoli_count = _count_gates(graph, GateName.CCX)
    single_qubit_percent = 0 if gate_count == 0 else single_gate_count / gate_count
    measure_count = _count_measured_qubits(graph)
    measure_percent = 0 if graph.is_empty() else measure_count / graph.height

    return DetailedMetrics(
        width=graph.height,
        depth=graph.width,
        max_density=_calculate_max_density(graph),
        average_density=_calculate_average_density(graph),
        x_count=x_count,
        y_count=y_count,
        z_count=z_count,
        pauli_count=pauli_count,
        hadamard_count=hadamard_count,
        initial_superposition_percent=_calculate_superposition_percent(graph),
        single_qubit_count=_count_single_gates(graph),
        other_single_qubit_count=single_gate_count - pauli_count - hadamard_count,
        single_controlled_qubit_count=_count_single_controlled_gates(graph),
        swap_count=_count_gates(graph, GateName.SWAP),
        cnot_count=cnot_count,
        cnot_qubit_percent=_calculate_cnot_qubit_percent(graph),
        average_cnot=0 if graph.is_empty() else cnot_count / graph.height,
        max_cnot=_count_max_cnot(graph),
        toffoli_count=toffoli_count,
        toffoli_qubit_percent=_calculate_toffoli_qubit_percent(graph),
        average_toffoli=0 if graph.is_empty() else toffoli_count / graph.height,
        max_toffoli=_count_max_toffoli(graph),
        gate_count=gate_count,
        controlled_gate_count=_count_controlled_gates(graph),
        single_qubit_percent=single_qubit_percent,
        measure_count=measure_count,
        measure_percent=measure_percent,
        ancilla_percent=1 - measure_percent,
    )


def _count_total_gates(graph: QuantumGraph) -> int:
    if graph.is_empty():
        return 0

    return sum(_count_gates(graph, gate_name) for gate_name in GateName)


def _count_gates(nodes: Iterable[GraphNode], gate_name: GateName) -> int:
    if gate_name.number_of_qubits() == 0:
        return 0

    return len([node for node in nodes if node.name == gate_name]) // gate_name.number_of_qubits()


def _calculate_superposition_percent(graph: QuantumGraph) -> float:
    if graph.is_empty():
        return 0

    first_column = _get_column(graph, 0)
    hadamard_count = _count_gates(first_column, GateName.H)

    return hadamard_count / graph.height


def _count_single_gates(graph: QuantumGraph) -> int:
    return sum([_count_gates(graph, gate_name) for gate_name in _SINGLE_QUBIT_GATES])


def _calculate_max_density(graph: QuantumGraph) -> int:
    max_density = 0

    for column_index in range(graph.width):
        density = _calculate_column_density(graph, column_index)
        max_density = max(max_density, density)

    return max_density


def _calculate_column_density(graph: QuantumGraph, column_index: int) -> int:
    column = _get_column(graph, column_index)
    gate_names = {node.name for node in column}
    return sum([_count_gates(column, gate_name) for gate_name in gate_names])


def _get_column(graph: QuantumGraph, column_index: int) -> list[GraphNode]:
    column = []

    for row_index in range(graph.height):
        position = Position(row_index, column_index)

        if not graph.has_node_at(position):
            continue

        column.append(graph[position])

    return column


def _calculate_average_density(graph: QuantumGraph) -> float:
    if graph.is_empty():
        return 0

    densities = [_calculate_column_density(graph, column) for column in range(graph.width)]
    return sum(densities) / len(densities)


def _count_single_controlled_gates(graph: QuantumGraph) -> int:
    return sum([_count_gates(graph, gate_name) for gate_name in _SINGLE_CONTROLLED_GATES])


def _count_controlled_gates(graph: QuantumGraph) -> int:
    return sum([_count_gates(graph, gate_name) for gate_name in _CONTROLLED_GATES])


def _calculate_cnot_qubit_percent(graph: QuantumGraph) -> float:
    if graph.is_empty():
        return 0

    rows_with_cnot = {node.position.row for node in graph if node.name == GateName.CX}
    return len(rows_with_cnot) / graph.height


def _count_max_cnot(graph: QuantumGraph) -> int:
    if graph.is_empty():
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


def _calculate_toffoli_qubit_percent(graph: QuantumGraph) -> float:
    if graph.is_empty():
        return 0

    rows_with_toffoli = {node.position.row for node in graph if node.name == GateName.CCX}
    return len(rows_with_toffoli) / graph.height


def _count_max_toffoli(graph: QuantumGraph) -> int:
    if graph.is_empty():
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


def _count_rotation_gates(graph: QuantumGraph) -> int:
    return sum([_count_gates(graph, gate_name) for gate_name in _ROTATION_GATES])


def _count_square_root_gates(graph: QuantumGraph) -> int:
    return sum([_count_gates(graph, gate_name) for gate_name in _SQUARE_ROOT_GATES])


def _count_measured_qubits(graph: QuantumGraph) -> int:
    if graph.is_empty():
        return 0

    measured_rows = {node.position.row for node in graph if node.name == GateName.MEASURE}
    return len(measured_rows)


def _count_gate_types(graph: QuantumGraph) -> int:
    types = {node.name for node in graph if node.name != GateName.ID}
    return len(types)
