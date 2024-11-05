from qiskit import QuantumCircuit

from qsimplify.analyzer import Analyzer, QuantumMetrics
from qsimplify.converter import Converter

converter = Converter()
analyzer = Analyzer(converter)

class TestAnalyzer:
    @staticmethod
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
            pauli_x_count=0,
            pauli_y_count=0,
            pauli_z_count=0,
            pauli_count=0,
            hadamard_count=0,
            initial_superposition_percent=0.0,
            other_single_gates_count=0,
            single_gate_count=0,
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
            single_gate_percent=1.0,
            measure_count=0,
            measure_percent=0.0,
            ancilla_percent=0.0,
        )

        print(metrics)
        print(expected_metrics)

        assert metrics == expected_metrics

    @staticmethod
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
            pauli_x_count=0,
            pauli_y_count=0,
            pauli_z_count=0,
            pauli_count=0,
            hadamard_count=2,
            initial_superposition_percent=0.3333,
            other_single_gates_count=2,
            single_gate_count=4,
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
            single_gate_percent=0.5,
            measure_count=2,
            measure_percent=0.6667,
            ancilla_percent=0.3333,
        )

        print(metrics)
        print(expected_metrics)

        assert metrics == expected_metrics
