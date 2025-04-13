from qiskit import QuantumCircuit

from qsimplify.analyzer import Analyzer, QuantumMetrics
from qsimplify.converter import Converter

converter = Converter()
analyzer = Analyzer(converter)


def test_empty_width():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.width == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.width == 0


def test_width():
    circuit = QuantumCircuit(2)
    circuit.x(0)
    circuit.x(1)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.width == 2

    circuit = QuantumCircuit(5)
    circuit.x(0)
    circuit.x(1)
    circuit.x(2)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.width == 3

    circuit = QuantumCircuit(5)
    circuit.x(0)
    circuit.x(1)
    circuit.x(4)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.width == 3


def test_empty_depth():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.depth == 0

    circuit = QuantumCircuit(4)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.depth == 0


def test_depth():
    circuit = QuantumCircuit(2)
    circuit.x(0)
    circuit.x(1)
    circuit.x(1)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.depth == 2

    circuit = QuantumCircuit(2)
    circuit.x(0)
    circuit.x(0)
    circuit.x(0)
    circuit.x(0)
    circuit.x(0)
    circuit.x(0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.depth == 6


def test_empty_max_density():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_density == 0

    circuit = QuantumCircuit(4)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_density == 0


def test_single_qubit_max_density():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.h(0)
    circuit.h(0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_density == 1

    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.h(1)
    circuit.h(1)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_density == 2


def test_multi_qubit_max_density():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.ch(0, 1)
    circuit.ch(1, 0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_density == 1

    circuit = QuantumCircuit(4)
    circuit.h(0)
    circuit.ch(1, 2)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_density == 2

    circuit = QuantumCircuit(4)
    circuit.ch(0, 1)
    circuit.ch(2, 3)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_density == 2

    circuit = QuantumCircuit(3)
    circuit.ccx(0, 1, 2)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_density == 1


def test_empty_average_density():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_density == 0

    circuit = QuantumCircuit(4)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_density == 0


def test_single_qubit_average_density():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.h(0)
    circuit.h(0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_density == 1

    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.h(1)
    circuit.h(1)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_density == 1.5


def test_multi_qubit_max_density():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.ch(0, 1)
    circuit.ch(1, 0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_density == 1

    circuit = QuantumCircuit(4)
    circuit.ch(0, 1)
    circuit.x(0)
    circuit.ch(2, 3)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_density == 1.5

    circuit = QuantumCircuit(3)
    circuit.z(1)
    circuit.ccx(0, 1, 2)
    circuit.z(2)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_density == 1


def test_empty_x_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.x_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.x_count == 0


def test_x_count():
    circuit = QuantumCircuit(2)
    circuit.x(0)
    circuit.y(0)
    circuit.z(1)
    circuit.x(0)
    circuit.h(1)
    circuit.x(1)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.x_count == 3


def test_empty_y_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.y_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.y_count == 0


def test_y_count():
    circuit = QuantumCircuit(2)
    circuit.x(0)
    circuit.y(0)
    circuit.z(1)
    circuit.x(0)
    circuit.y(1)
    circuit.h(1)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.y_count == 2


def test_empty_z_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.z_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.z_count == 0


def test_z_count():
    circuit = QuantumCircuit(2)
    circuit.z(0)
    circuit.y(0)
    circuit.z(1)
    circuit.x(0)
    circuit.h(1)
    circuit.z(1)
    circuit.z(0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.z_count == 4


def test_empty_pauli_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.pauli_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.pauli_count == 0


def test_pauli_count():
    circuit = QuantumCircuit(2)
    circuit.h(1)
    circuit.x(0)
    circuit.y(0)
    circuit.swap(0, 1)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.z(1)
    circuit.x(0)
    circuit.cz(0, 1)
    circuit.z(1)
    circuit.h(1)
    circuit.x(1)
    circuit.h(1)
    circuit.cx(1, 0)
    circuit.y(0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.pauli_count == 7


def test_empty_hadamard_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.hadamard_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.hadamard_count == 0


def test_hadamard_count():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.y(0)
    circuit.z(1)
    circuit.x(0)
    circuit.h(1)
    circuit.h(0)
    circuit.z(1)
    circuit.h(0)
    circuit.h(1)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.hadamard_count == 5


def test_empty_initial_superposition_percent():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.initial_superposition_percent == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.initial_superposition_percent == 0


def test_initial_superposition_percent():
    circuit = QuantumCircuit(4)

    circuit.h(0)
    circuit.h(1)
    circuit.x(2)
    circuit.x(3)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.initial_superposition_percent == 0.5

    circuit = QuantumCircuit(4)

    circuit.h(0)
    circuit.h(1)
    circuit.x(2)
    circuit.h(3)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.initial_superposition_percent == 0.75

    circuit = QuantumCircuit(1)

    circuit.h(0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.initial_superposition_percent == 1



def test_empty_other_single_qubit_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.other_single_qubit_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.other_single_qubit_count == 0


def test_other_single_qubit_count():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.rx(0.5, 0)
    circuit.z(1)
    circuit.x(0)
    circuit.h(1)
    circuit.rz(0.25, 1)
    circuit.z(1)
    circuit.ry(0.75, 0)
    circuit.h(1)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.other_single_qubit_count == 3


def test_empty_single_qubit_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.single_qubit_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.single_qubit_count == 0

def test_single_qubit_count():
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.cz(0, 1)
    circuit.rx(0.5, 0)
    circuit.z(1)
    circuit.x(0)
    circuit.cx(0, 1)
    circuit.h(1)
    circuit.rz(0.25, 1)
    circuit.z(1)
    circuit.ry(0.75, 0)
    circuit.swap(0, 1)
    circuit.h(1)
    circuit.y(0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.single_qubit_count == 10


def test_empty_single_controlled_qubit_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.single_controlled_qubit_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.single_controlled_qubit_count == 0

def test_single_controlled_qubit_count():
    circuit = QuantumCircuit(3)

    circuit.h(0)
    circuit.cz(0, 1)
    circuit.ch(1, 0)
    circuit.z(2)
    circuit.x(2)
    circuit.cx(0, 1)
    circuit.swap(1, 2)
    circuit.cswap(0, 2, 1)
    circuit.ccx(2, 1, 0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.single_qubit_count == 3


def test_empty_swap_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.swap_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.swap_count == 0

def test_swap_count():
    circuit = QuantumCircuit(2)
    circuit.cx(0, 1)
    circuit.swap(0, 1)
    circuit.cz(1, 0)
    circuit.swap(1, 0)
    circuit.ch(0, 1)
    circuit.swap(1, 0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.swap_count == 3


def test_empty_cnot_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.cnot_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.cnot_count == 0


def test_cnot_count():
    circuit = QuantumCircuit(2)
    circuit.cx(0, 1)
    circuit.swap(0, 1)
    circuit.cz(1, 0)
    circuit.cx(1, 0)
    circuit.ch(0, 1)
    circuit.swap(1, 0)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.cnot_count == 2


def test_empty_cnot_qubit_percent():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.cnot_qubit_percent == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.cnot_qubit_percent == 0


def test_cnot_qubit_percent():
    circuit = QuantumCircuit(5)
    circuit.cx(0, 1)
    circuit.z(2)
    circuit.x(3)
    circuit.cx(1, 4)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.cnot_qubit_percent == 0.6

    circuit = QuantumCircuit(5)
    circuit.cx(0, 1)
    circuit.cx(2, 1)
    circuit.cx(3, 1)
    circuit.cx(4, 1)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.cnot_qubit_percent == 1


def test_empty_average_cnot():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_cnot == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_cnot == 0


def test_average_cnot():
    circuit = QuantumCircuit(5)
    circuit.cx(0, 1)
    circuit.cx(0, 3)
    circuit.cx(2, 3)
    circuit.cx(0, 4)
    circuit.cx(0, 1)
    circuit.cx(1, 3)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_cnot == 1.2


def test_empty_max_cnot():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_cnot == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_cnot == 0

def test_max_cnot():
    circuit = QuantumCircuit(5)
    circuit.cx(0, 1)
    circuit.cx(0, 3)
    circuit.cx(2, 3)
    circuit.cx(0, 4)
    circuit.cx(0, 1)
    circuit.cx(1, 3)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_cnot == 3


def test_max_cnot_without_cnots():
    circuit = QuantumCircuit(3)
    circuit.x(0)
    circuit.y(1)
    circuit.z(2)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_cnot == 0


def test_empty_toffoli_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.toffoli_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.toffoli_count == 0


def test_toffoli_count():
    circuit = QuantumCircuit(3)
    circuit.ccx(0, 1, 2)
    circuit.cx(0, 1)
    circuit.cz(1, 2)
    circuit.ccx(0, 1, 2)
    circuit.swap(0, 1)
    circuit.cz(1, 0)
    circuit.ccx(0, 2, 1)
    circuit.swap(1, 0)
    circuit.ch(0, 1)
    circuit.cswap(0, 1, 2)
    circuit.swap(1, 0)
    circuit.ccx(0, 2, 1)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.toffoli_count == 4

def test_empty_toffoli_qubit_percent():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.toffoli_qubit_percent == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.toffoli_qubit_percent == 0


def test_toffoli_qubit_percent():
    circuit = QuantumCircuit(5)
    circuit.h(0)
    circuit.ccx(1, 2, 3)
    circuit.h(4)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.toffoli_qubit_percent == 0.6

    circuit = QuantumCircuit(5)
    circuit.ccx(0, 1, 4)
    circuit.ccx(1, 2, 3)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.toffoli_qubit_percent == 1


def test_empty_average_toffoli():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_toffoli == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_toffoli == 0


def test_average_toffoli():
    circuit = QuantumCircuit(5)
    circuit.h(0)
    circuit.ccx(1, 2, 3)
    circuit.h(4)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_toffoli == 0.2

    circuit = QuantumCircuit(5)
    circuit.z(0)
    circuit.ccx(1, 2, 3)
    circuit.ccx(2, 3, 4)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.average_toffoli == 0.4

def test_empty_max_toffoli():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_toffoli == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_toffoli == 0


def test_max_toffoli():
    circuit = QuantumCircuit(3)
    circuit.ccx(0, 1, 2)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_toffoli == 1

    circuit = QuantumCircuit(4)
    circuit.ccx(0, 1, 2)
    circuit.ccx(3, 1, 2)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.max_toffoli == 2


def test_empty_gate_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.gate_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.gate_count == 0

def test_gate_count():
    circuit = QuantumCircuit(3)

    circuit.x(1)
    circuit.ccx(0, 1, 2)
    circuit.rx(0.5, 2)
    circuit.cx(0, 1)
    circuit.cz(1, 2)
    circuit.y(0)
    circuit.ccx(0, 1, 2)
    circuit.swap(0, 1)
    circuit.cz(1, 0)
    circuit.rz(0.5, 2)
    circuit.swap(1, 0)
    circuit.ch(0, 1)
    circuit.h(2)
    circuit.cswap(0, 1, 2)
    circuit.swap(1, 0)
    circuit.ry(0.25, 1)
    circuit.ccx(0, 2, 1)
    circuit.z(2)
    circuit.measure_all()

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.gate_count == 21


def test_empty_controlled_gate_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.controlled_gate_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.controlled_gate_count == 0

def test_controlled_gate_count():
    circuit = QuantumCircuit(3)

    circuit.h(0)
    circuit.ch(0, 1)
    circuit.x(1)
    circuit.cx(1, 2)
    circuit.z(2)
    circuit.cz(1, 2)
    circuit.y(0)
    circuit.ccx(0, 1, 2)
    circuit.swap(0, 1)
    circuit.cswap(0, 1, 2)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.controlled_gate_count == 5


def test_empty_single_qubit_gate_percent():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.single_qubit_percent == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.single_qubit_percent == 0


def test_single_qubit_gate_percent():
    circuit = QuantumCircuit(3)
    circuit.x(0)
    circuit.h(1)
    circuit.h(2)
    circuit.cx(1, 2)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.single_qubit_percent == 0.75

    circuit = QuantumCircuit(4)
    circuit.x(0)
    circuit.h(1)
    circuit.h(2)
    circuit.cx(2, 3)
    circuit.cx(1, 0)
    circuit.cz(0, 2)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.single_qubit_percent == 0.5


def test_empty_measure_count():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.measure_count == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.measure_count == 0


def test_measure_count():
    circuit = QuantumCircuit(4)
    circuit.measure_all()

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.measure_count == 4

    circuit = QuantumCircuit(4, 2)
    circuit.measure(0, 0)
    circuit.x(1)
    circuit.measure(2, 1)
    circuit.z(3)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.measure_count == 2


def test_empty_measure_percent():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.measure_percent == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.measure_percent == 0


def test_measure_percent():
    circuit = QuantumCircuit(4)
    circuit.measure_all()

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.measure_percent == 1

    circuit = QuantumCircuit(4, 1)
    circuit.measure(0, 0)
    circuit.x(1)
    circuit.y(2)
    circuit.z(3)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.measure_percent == 0.25


def test_empty_ancilla_percent():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.ancilla_percent == 1

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.ancilla_percent == 1


def test_ancilla_percent():
    circuit = QuantumCircuit(4, 1)
    circuit.measure(0, 0)
    circuit.x(1)
    circuit.y(2)
    circuit.z(3)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.ancilla_percent == 0.75

    circuit = QuantumCircuit(4)
    circuit.measure_all()

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))
    assert metrics.ancilla_percent == 0


def test_example_b_metrics():
    circuit = QuantumCircuit(5)

    circuit.cx(0, 1)
    circuit.cx(0, 3)
    circuit.cx(2, 3)
    circuit.ccx(1, 3, 4)
    circuit.cx(0, 4)
    circuit.cx(0, 1)
    circuit.cx(1, 3)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))

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
    circuit = QuantumCircuit(3, 2)

    circuit.h(1)
    circuit.cx(1, 2)
    circuit.cx(0, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    circuit.measure(1, 1)
    circuit.cx(1, 2)
    circuit.cz(0, 2)

    metrics = analyzer.calculate_metrics(converter.circuit_to_graph(circuit))

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
