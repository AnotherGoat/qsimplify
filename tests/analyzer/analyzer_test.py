from qsimplify.analyzer import QuantumMetrics, analyzer
from qsimplify.model import GraphBuilder


def test_empty_width():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.width == 0


def test_width():
    graph = GraphBuilder().push_x(0).push_x(1).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.width == 2

    graph = GraphBuilder().push_x(0).push_x(1).push_x(2).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.width == 3

    graph = GraphBuilder().push_x(0).push_x(1).push_x(4).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.width == 3


def test_empty_depth():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.depth == 0


def test_depth():
    graph = GraphBuilder().push_x(0).push_x(1).push_x(1).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.depth == 2

    graph = (
        GraphBuilder()
        .push_x(0)
        .push_x(0)
        .push_x(0)
        .push_x(0)
        .push_x(0)
        .push_x(0)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.depth == 6


def test_empty_max_density():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_density == 0


def test_single_qubit_max_density():
    graph = GraphBuilder().push_h(0).push_h(0).push_h(0).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_density == 1

    graph = GraphBuilder().push_h(0).push_h(1).push_h(1).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_density == 2


def test_multi_qubit_max_density():
    graph = GraphBuilder().push_h(0).push_ch(0, 1).push_ch(1, 0).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_density == 1

    graph = GraphBuilder().push_h(0).push_ch(1, 2).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_density == 2

    graph = GraphBuilder().push_ch(0, 1).push_ch(2, 3).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_density == 2

    graph = GraphBuilder().push_ccx(0, 1, 2).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_density == 1


def test_empty_average_density():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.average_density == 0


def test_single_qubit_average_density():
    graph = GraphBuilder().push_h(0).push_h(0).push_h(0).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.average_density == 1

    graph = GraphBuilder().push_h(0).push_h(1).push_h(1).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.average_density == 1.5


def test_multi_qubit_average_density():
    graph = GraphBuilder().push_h(0).push_ch(0, 1).push_ch(1, 0).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.average_density == 1

    graph = GraphBuilder().push_ch(0, 1).push_x(0).push_ch(2, 3).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.average_density == 1.5

    graph = GraphBuilder().push_z(1).push_ccx(0, 1, 2).push_z(2).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.average_density == 1


def test_empty_x_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.x_count == 0


def test_x_count():
    graph = (
        GraphBuilder()
        .push_x(0)
        .push_y(0)
        .push_z(1)
        .push_x(0)
        .push_h(1)
        .push_x(1)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.x_count == 3


def test_empty_y_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.y_count == 0


def test_y_count():
    graph = (
        GraphBuilder()
        .push_x(0)
        .push_y(0)
        .push_z(1)
        .push_x(0)
        .push_y(1)
        .push_h(1)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.y_count == 2


def test_empty_z_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.z_count == 0


def test_z_count():
    graph = (
        GraphBuilder()
        .push_z(0)
        .push_y(0)
        .push_z(1)
        .push_x(0)
        .push_h(1)
        .push_z(1)
        .push_z(0)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.z_count == 4


def test_empty_pauli_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.pauli_count == 0


def test_pauli_count():
    graph = (
        GraphBuilder()
        .push_h(1)
        .push_x(0)
        .push_y(0)
        .push_swap(0, 1)
        .push_h(0)
        .push_cx(0, 1)
        .push_z(1)
        .push_x(0)
        .push_cz(0, 1)
        .push_z(1)
        .push_h(1)
        .push_x(1)
        .push_h(1)
        .push_cx(1, 0)
        .push_y(0)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.pauli_count == 7


def test_empty_hadamard_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.hadamard_count == 0


def test_hadamard_count():
    graph = (
        GraphBuilder()
        .push_h(0)
        .push_y(0)
        .push_z(1)
        .push_x(0)
        .push_h(1)
        .push_h(0)
        .push_z(1)
        .push_h(0)
        .push_h(1)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.hadamard_count == 5


def test_empty_initial_superposition_percent():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.initial_superposition_percent == 0


def test_initial_superposition_percent():
    graph = GraphBuilder().push_h(0).push_h(1).push_x(2).push_x(3).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.initial_superposition_percent == 0.5

    graph = GraphBuilder().push_h(0).push_h(1).push_x(2).push_h(3).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.initial_superposition_percent == 0.75

    graph = GraphBuilder().push_h(0).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.initial_superposition_percent == 1


def test_empty_other_single_qubit_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.other_single_qubit_count == 0


def test_other_single_qubit_count():
    graph = (
        GraphBuilder()
        .push_h(0)
        .push_rx(0.5, 0)
        .push_z(1)
        .push_x(0)
        .push_h(1)
        .push_rz(0.25, 1)
        .push_z(1)
        .push_ry(0.75, 0)
        .push_h(1)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.other_single_qubit_count == 3


def test_empty_single_qubit_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.single_qubit_count == 0


def test_single_qubit_count():
    graph = (
        GraphBuilder()
        .push_h(0)
        .push_cz(0, 1)
        .push_rx(0.5, 0)
        .push_z(1)
        .push_x(0)
        .push_cx(0, 1)
        .push_h(1)
        .push_rz(0.25, 1)
        .push_z(1)
        .push_ry(0.75, 0)
        .push_swap(0, 1)
        .push_h(1)
        .push_y(0)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.single_qubit_count == 10


def test_empty_single_controlled_qubit_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.single_controlled_qubit_count == 0


def test_single_controlled_qubit_count():
    graph = (
        GraphBuilder()
        .push_h(0)
        .push_cz(0, 1)
        .push_ch(1, 0)
        .push_z(2)
        .push_x(2)
        .push_cx(0, 1)
        .push_swap(1, 2)
        .push_cswap(0, 2, 1)
        .push_ccx(2, 1, 0)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.single_qubit_count == 3


def test_empty_swap_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.swap_count == 0


def test_swap_count():
    graph = (
        GraphBuilder()
        .push_cx(0, 1)
        .push_swap(0, 1)
        .push_cz(1, 0)
        .push_swap(1, 0)
        .push_ch(0, 1)
        .push_swap(1, 0)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.swap_count == 3


def test_empty_cnot_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.cnot_count == 0


def test_cnot_count():
    graph = (
        GraphBuilder()
        .push_cx(0, 1)
        .push_swap(0, 1)
        .push_cz(1, 0)
        .push_cx(1, 0)
        .push_ch(0, 1)
        .push_swap(1, 0)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.cnot_count == 2


def test_empty_cnot_qubit_percent():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.cnot_qubit_percent == 0


def test_cnot_qubit_percent():
    graph = GraphBuilder().push_cx(0, 1).push_z(2).push_x(3).push_cx(1, 4).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.cnot_qubit_percent == 0.6

    graph = GraphBuilder().push_cx(0, 1).push_cx(2, 1).push_cx(3, 1).push_cx(4, 1).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.cnot_qubit_percent == 1


def test_empty_average_cnot():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.average_cnot == 0


def test_average_cnot():
    graph = (
        GraphBuilder()
        .push_cx(0, 1)
        .push_cx(0, 3)
        .push_cx(2, 3)
        .push_cx(0, 4)
        .push_cx(0, 1)
        .push_cx(1, 3)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.average_cnot == 1.2


def test_empty_max_cnot():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_cnot == 0


def test_max_cnot():
    graph = (
        GraphBuilder()
        .push_cx(0, 1)
        .push_cx(0, 3)
        .push_cx(2, 3)
        .push_cx(0, 4)
        .push_cx(0, 1)
        .push_cx(1, 3)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_cnot == 3


def test_max_cnot_without_cnots():
    graph = GraphBuilder().push_x(0).push_y(1).push_z(2).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_cnot == 0


def test_empty_toffoli_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.toffoli_count == 0


def test_toffoli_count():
    graph = (
        GraphBuilder()
        .push_ccx(0, 1, 2)
        .push_cx(0, 1)
        .push_cz(1, 2)
        .push_ccx(0, 1, 2)
        .push_swap(0, 1)
        .push_cz(1, 0)
        .push_ccx(0, 2, 1)
        .push_swap(1, 0)
        .push_ch(0, 1)
        .push_cswap(0, 1, 2)
        .push_swap(1, 0)
        .push_ccx(0, 2, 1)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.toffoli_count == 4


def test_empty_toffoli_qubit_percent():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.toffoli_qubit_percent == 0


def test_toffoli_qubit_percent():
    graph = GraphBuilder().push_h(0).push_ccx(1, 2, 3).push_h(4).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.toffoli_qubit_percent == 0.6

    graph = GraphBuilder().push_ccx(0, 1, 4).push_ccx(1, 2, 3).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.toffoli_qubit_percent == 1


def test_empty_average_toffoli():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.average_toffoli == 0


def test_average_toffoli():
    graph = GraphBuilder().push_h(0).push_ccx(1, 2, 3).push_h(4).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.average_toffoli == 0.2

    graph = GraphBuilder().push_z(0).push_ccx(1, 2, 3).push_ccx(2, 3, 4).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.average_toffoli == 0.4


def test_empty_max_toffoli():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_toffoli == 0


def test_max_toffoli():
    graph = GraphBuilder().push_ccx(0, 1, 2).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_toffoli == 1

    graph = GraphBuilder().push_ccx(0, 1, 2).push_ccx(3, 1, 2).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.max_toffoli == 2


def test_empty_gate_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.gate_count == 0


def test_gate_count():
    graph = (
        GraphBuilder()
        .push_x(1)
        .push_ccx(0, 1, 2)
        .push_rx(0.5, 2)
        .push_cx(0, 1)
        .push_cz(1, 2)
        .push_y(0)
        .push_ccx(0, 1, 2)
        .push_swap(0, 1)
        .push_cz(1, 0)
        .push_rz(0.5, 2)
        .push_swap(1, 0)
        .push_ch(0, 1)
        .push_h(2)
        .push_cswap(0, 1, 2)
        .push_swap(1, 0)
        .push_ry(0.25, 1)
        .push_ccx(0, 2, 1)
        .push_z(2)
        .measure_all()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.gate_count == 21


def test_empty_controlled_gate_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.controlled_gate_count == 0


def test_controlled_gate_count():
    graph = (
        GraphBuilder()
        .push_h(0)
        .push_ch(0, 1)
        .push_x(1)
        .push_cx(1, 2)
        .push_z(2)
        .push_cz(1, 2)
        .push_y(0)
        .push_ccx(0, 1, 2)
        .push_swap(0, 1)
        .push_cswap(0, 1, 2)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.controlled_gate_count == 5


def test_empty_single_qubit_gate_percent():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.single_qubit_percent == 0


def test_single_qubit_gate_percent():
    graph = GraphBuilder().push_x(0).push_h(1).push_h(2).push_cx(1, 2).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.single_qubit_percent == 0.75

    graph = GraphBuilder().push_x(0).push_h(1).push_h(2).push_cx(2, 3).push_cx(1, 0).push_cz(0, 2).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.single_qubit_percent == 0.5


def test_empty_measure_count():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.measure_count == 0


def test_measure_count():
    graph = GraphBuilder().push_measure(0, 0).push_measure(1, 1).push_measure(2, 2).push_measure(3, 3).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.measure_count == 4

    graph = GraphBuilder().push_measure(0, 0).push_x(1).push_measure(2, 1).push_z(3).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.measure_count == 2


def test_empty_measure_percent():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.measure_percent == 0


def test_measure_percent():
    graph = GraphBuilder().push_measure(0, 0).push_measure(1, 1).push_measure(2, 2).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.measure_percent == 1

    graph = GraphBuilder().push_measure(0, 0).push_x(1).push_y(2).push_z(3).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.measure_percent == 0.25


def test_empty_ancilla_percent():
    graph = GraphBuilder().build()
    metrics = analyzer.calculate_metrics(graph)
    assert metrics.ancilla_percent == 1


def test_ancilla_percent():
    graph = GraphBuilder().push_measure(0, 0).push_x(1).push_y(2).push_z(3).build()

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.ancilla_percent == 0.75

    graph = (
        GraphBuilder()
        .push_measure(0, 0)
        .push_measure(1, 1)
        .push_measure(2, 2)
        .push_measure(3, 3)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)
    assert metrics.ancilla_percent == 0


def test_example_b_metrics():
    graph = (
        GraphBuilder()
        .push_cx(0, 1)
        .push_cx(0, 3)
        .push_cx(2, 3)
        .push_ccx(1, 3, 4)
        .push_cx(0, 4)
        .push_cx(0, 1)
        .push_cx(1, 3)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)

    expected_metrics = QuantumMetrics(
        width=5,
        depth=7,
        max_density=1,
        average_density=1.0,
        x_count=0,
        y_count=0,
        z_count=0,
        pauli_count=0,
        hadamard_count=0,
        initial_superposition_percent=0.0,
        other_single_qubit_count=0,
        single_qubit_count=0,
        single_controlled_qubit_count=0,
        swap_count=0,
        cnot_count=6,
        cnot_qubit_percent=1.0,
        average_cnot=1.2,
        max_cnot=3,
        toffoli_count=1,
        toffoli_qubit_percent=0.6,
        average_toffoli=0.2,
        max_toffoli=1,
        gate_count=7,
        controlled_gate_count=7,
        single_qubit_percent=1.0,
        measure_count=0,
        measure_percent=0.0,
        ancilla_percent=0.0,
    )

    assert metrics == expected_metrics


def test_visualization_example_metrics():
    graph = (
        GraphBuilder()
        .push_h(1)
        .push_cx(1, 2)
        .push_cx(0, 1)
        .push_h(0)
        .push_measure(0, 0)
        .push_measure(1, 1)
        .push_cx(1, 2)
        .push_cz(0, 2)
        .build()
    )

    metrics = analyzer.calculate_metrics(graph)

    expected_metrics = QuantumMetrics(
        width=3,
        depth=7,
        max_density=2,
        average_density=1.1429,
        x_count=0,
        y_count=0,
        z_count=0,
        pauli_count=0,
        hadamard_count=2,
        initial_superposition_percent=1 / 3,
        other_single_qubit_count=2,
        single_qubit_count=4,
        single_controlled_qubit_count=1,
        swap_count=0,
        cnot_count=3,
        cnot_qubit_percent=1.0,
        average_cnot=1.0,
        max_cnot=2,
        toffoli_count=0,
        toffoli_qubit_percent=0.0,
        average_toffoli=0.0,
        max_toffoli=0,
        gate_count=8,
        controlled_gate_count=4,
        single_qubit_percent=0.5,
        measure_count=2,
        measure_percent=2 / 3,
        ancilla_percent=1 / 3,
    )

    assert metrics == expected_metrics
