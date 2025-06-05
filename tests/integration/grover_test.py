from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from qsimplify.converter.qiskit_converter import QiskitConverter
from qsimplify.simplifier import Simplifier


def test_grover_2_qubits():
    polluted = QuantumCircuit(2)

    # Superposition
    polluted.h(range(2))
    polluted.barrier()

    # 11 Oracle
    polluted.cz(0, 1)
    polluted.barrier()

    # Diffusion operator
    polluted.h(range(2))
    polluted.x(range(2))
    polluted.h(1)
    polluted.cx(0, 1)
    polluted.x(0)
    polluted.h(1)
    polluted.h(0)
    polluted.x(1)
    polluted.h(1)

    # Measurement
    polluted.measure_all()

    expected = QuantumCircuit(2)

    expected.h(1)
    expected.cx(1, 0)
    expected.x(0)
    expected.z(1)
    expected.cx(0, 1)
    expected.x(0)
    expected.z(1)
    expected.h(0)

    # Measurement
    expected.measure_all()

    simplifier = Simplifier()
    converter = QiskitConverter()

    graph = converter.to_graph(polluted)
    simplified_graph = simplifier.simplify_graph(graph)
    simplified = converter.from_graph(simplified_graph)

    simplified.remove_final_measurements()
    expected.remove_final_measurements()
    assert Operator(simplified).equiv(Operator(expected))
