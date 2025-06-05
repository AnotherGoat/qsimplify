import numpy
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Operator

from qsimplify.converter.qiskit_converter import QiskitConverter
from qsimplify.simplifier import Simplifier


def test_qft_3_qubits():
    circuit = QuantumCircuit(3)

    # Initial state
    circuit.h(range(3))
    circuit.p(numpy.pi / 2, 0)
    circuit.p(numpy.pi / 4, 1)
    circuit.p(numpy.pi / 2, 2)
    circuit.barrier()

    # QFT
    circuit.compose(QFT(3).decompose(), qubits=range(3), inplace=True)

    # Measurement
    circuit.measure_all()

    polluted = QuantumCircuit(3)

    # Initial state
    polluted.h(range(3))
    polluted.p(numpy.pi / 2, 0)
    polluted.p(numpy.pi / 4, 1)
    polluted.p(numpy.pi / 2, 2)
    polluted.barrier()

    # Polluted QFT
    polluted.cz(0, 1)
    polluted.h(2)
    polluted.z(0)
    polluted.cz(0, 1)
    polluted.z(0)
    polluted.cp(numpy.pi / 2, 1, 2)
    polluted.h(1)
    polluted.y(2)
    polluted.y(2)
    polluted.cp(numpy.pi / 4, 0, 2)
    polluted.cp(numpy.pi / 2, 0, 1)
    polluted.h(0)
    polluted.cx(0, 2)
    polluted.cx(2, 0)
    polluted.cx(0, 2)

    # Measurement
    polluted.measure_all()

    simplifier = Simplifier()
    converter = QiskitConverter()

    graph = converter.to_graph(polluted)
    simplified_graph = simplifier.simplify_graph(graph, iterations=2)
    simplified = converter.from_graph(simplified_graph)

    circuit.remove_final_measurements()
    simplified.remove_final_measurements()
    assert Operator(circuit).equiv(Operator(simplified))
