from qiskit import QuantumCircuit

from qsimplify.analyzer import Analyzer, QuantumMetrics
from qsimplify.converter import Converter

converter = Converter()
analyzer = Analyzer(converter)

def test_empty_width():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.width == 0

    circuit = QuantumCircuit(5)
    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.width == 0

def test_width():
    circuit = QuantumCircuit(2)
    circuit.x(0)
    circuit.x(1)

    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.width == 2

    circuit = QuantumCircuit(5)
    circuit.x(0)
    circuit.x(1)
    circuit.x(2)

    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.width == 3

    # TODO: Instead of returning 5 for this case, remove empty qubits
    circuit = QuantumCircuit(5)
    circuit.x(0)
    circuit.x(1)
    circuit.x(4)

    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.width == 5


def test_empty_depth():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.depth == 0

    circuit = QuantumCircuit(4)
    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.depth == 0

def test_depth():
    circuit = QuantumCircuit(2)
    circuit.x(0)
    circuit.x(1)
    circuit.x(1)

    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.depth == 2

    circuit = QuantumCircuit(2)
    circuit.x(0)
    circuit.x(0)
    circuit.x(0)
    circuit.x(0)
    circuit.x(0)
    circuit.x(0)

    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.depth == 6

def test_empty_max_density():
    circuit = QuantumCircuit(0)
    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.max_density == 0

    circuit = QuantumCircuit(4)
    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.max_density == 0

def test_single_qubit_max_density():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.h(0)
    circuit.h(0)

    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.max_density == 1

    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.h(1)
    circuit.h(1)

    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.max_density == 2

def test_multi_qubit_max_density():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.ch(0, 1)
    circuit.ch(1, 0)

    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.max_density == 1

    circuit = QuantumCircuit(4)
    circuit.h(0)
    circuit.ch(1, 2)

    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.max_density == 2

    circuit = QuantumCircuit(4)
    circuit.ch(0, 1)
    circuit.ch(2, 3)

    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.max_density == 2

    circuit = QuantumCircuit(3)
    circuit.ccx(0, 1, 2)

    metrics = analyzer.calculate_metrics(circuit)
    assert metrics.max_density == 1


def test_average_density():
    pass

def test_x_count():
    pass

def test_y_count():
    pass

def test_z_count():
    pass

def test_pauli_count():
    pass

def test_hadamard_count():
    pass

def test_initial_superposition_percent():
    pass

def test_other_single_qubit_count():
    pass

def test_single_qubit_count():
    pass

def test_controlled_single_qubit_count():
    pass

def test_controlled_multi_qubit_count():
    pass

def test_swap_count():
    pass

def test_cnot_count():
    pass

def test_cnot_qubit_percent():
    pass

def test_average_cnot():
    pass

def test_max_cnot():
    pass

def test_toffoli_count():
    pass

def test_toffoli_qubit_percent():
    pass

def test_average_toffoli():
    pass

def test_max_toffoli():
    pass

def test_gate_count():
    pass

def test_controlled_gate_count():
    pass

def test_single_qubit_gate_percent():
    pass

def test_measure_count():
    pass

def test_measure_percent():
    pass

def test_ancilla_percent():
    pass

def test_example_b_metrics():
    circuit = QuantumCircuit(5)

    circuit.cx(0, 1)
    circuit.cx(0, 3)
    circuit.cx(2, 3)
    circuit.ccx(1, 3, 4)
    circuit.cx(0, 4)
    circuit.cx(0, 1)
    circuit.cx(1, 3)

    metrics = analyzer.calculate_metrics(circuit)

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
        controlled_single_qubit_count=0,
        controlled_multi_qubit_count=7,
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

    print(metrics)
    print(expected_metrics)

    assert metrics == expected_metrics


def test_visualization_example_metrics():
    circuit = QuantumCircuit(3)

    circuit.h(1)
    circuit.cx(1, 2)
    circuit.cx(0, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    circuit.measure(1, 1)
    circuit.cx(1, 2)
    circuit.cz(0, 2)

    metrics = analyzer.calculate_metrics(circuit)

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
        initial_superposition_percent=0.3333,
        other_single_qubit_count=2,
        single_qubit_count=4,
        controlled_single_qubit_count=1,
        controlled_multi_qubit_count=7,
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
        measure_percent=0.6667,
        ancilla_percent=0.3333,
    )

    print(metrics)
    print(expected_metrics)

    assert metrics == expected_metrics
