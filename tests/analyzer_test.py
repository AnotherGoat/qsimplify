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
            average_density=1,
            pauli_x_count=0,
            pauli_y_count=0,
            pauli_z_count=0,
            pauli_count=0,
            hadamard_count=0,
            initial_superposition_rate=0,
            other_single_gates_count=0,
            single_gate_count=0,
            controlled_single_qubit_count=0,
            gate_count=7,
            controlled_gate_count=7,
            single_gate_rate=1,
        )

        print(metrics)
        print(expected_metrics)

        assert metrics == expected_metrics
