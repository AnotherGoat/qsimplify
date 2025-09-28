import numpy

from qsimplify.generator import QiskitGenerator
from qsimplify.model.graph_builder import GraphBuilder

generator = QiskitGenerator()


def test_generate_empty_circuit():
    graph = GraphBuilder().build()
    code = generator.generate(graph)

    assert (
        code
        == """
from qiskit import QuantumCircuit

circuit = QuantumCircuit()
""".strip()
    )


def test_generate_single_qubit_circuit():
    graph = GraphBuilder().push_h(0).push_x(0).push_y(0).push_z(0).push_t(0).build()
    code = generator.generate(graph)

    assert (
        code
        == """
from qiskit import QuantumCircuit

circuit = QuantumCircuit(1)
circuit.h(0)
circuit.x(0)
circuit.y(0)
circuit.z(0)
circuit.t(0)
""".strip()
    )


def test_generate_circuit_with_measurements():
    graph = GraphBuilder().push_h(0).push_measure(0, 0).build()
    code = generator.generate(graph)

    assert (
        code
        == """
from qiskit import QuantumCircuit

circuit = QuantumCircuit(1, 1)
circuit.h(0)
circuit.measure(0, 0)
""".strip()
    )


def test_generate_circuit_with_rotations():
    graph = (
        GraphBuilder()
        .push_rx(numpy.pi, 0)
        .push_ry(numpy.pi / 2, 0)
        .push_rz(2 * numpy.pi / 3, 0)
        .push_p(5 * numpy.pi / 4, 0)
        .build()
    )
    code = generator.generate(graph)

    assert (
        code
        == """
import numpy
from qiskit import QuantumCircuit

circuit = QuantumCircuit(1)
circuit.rx(numpy.pi, 0)
circuit.ry(numpy.pi / 2, 0)
circuit.rz(2 * numpy.pi / 3, 0)
circuit.p(5 * numpy.pi / 4, 0)
""".strip()
    )


def test_generate_circuit_with_zero_rotations():
    graph = GraphBuilder().push_p(0, 0).push_p(0.00000001, 0).build()
    code = generator.generate(graph)

    assert (
        code
        == """
from qiskit import QuantumCircuit

circuit = QuantumCircuit(1)
circuit.p(0, 0)
circuit.p(0, 0)
""".strip()
    )


def test_generate_circuit_with_uncommon_rotations():
    graph = (
        GraphBuilder()
        .push_rx(0.222, 0)
        .push_ry(1.333, 0)
        .push_rz(2.444, 0)
        .push_p(3.555, 0)
        .build()
    )
    code = generator.generate(graph)

    assert (
        code
        == """
from qiskit import QuantumCircuit

circuit = QuantumCircuit(1)
circuit.rx(0.222, 0)
circuit.ry(1.333, 0)
circuit.rz(2.444, 0)
circuit.p(3.555, 0)
""".strip()
    )


def test_generate_circuit_with_sy_gate():
    graph = GraphBuilder().push_sy(0).build()
    code = generator.generate(graph)

    assert (
        code
        == """
from qiskit import QuantumCircuit
from qiskit.circuit.library.standard_gates import YGate

circuit = QuantumCircuit(1)
circuit.append(YGate().power(1 / 2), [0])
""".strip()
    )


def test_generate_circuit_with_two_qubits():
    graph = GraphBuilder().push_cx(0, 1).push_cy(1, 0).push_cp(numpy.pi, 1, 0).build()
    code = generator.generate(graph)

    assert (
        code
        == """
import numpy
from qiskit import QuantumCircuit

circuit = QuantumCircuit(2)
circuit.cx(0, 1)
circuit.cy(1, 0)
circuit.cp(numpy.pi, 1, 0)
""".strip()
    )


def test_generate_circuit_orders_qubits():
    graph = GraphBuilder().push_h(4).push_x(2).push_y(0).push_z(1).push_s(3).build()
    code = generator.generate(graph)

    assert (
        code
        == """
from qiskit import QuantumCircuit

circuit = QuantumCircuit(5)
circuit.y(0)
circuit.z(1)
circuit.x(2)
circuit.s(3)
circuit.h(4)
""".strip()
    )


def test_generate_circuit_orders_symmetrical_gates():
    graph = GraphBuilder().push_swap(1, 0).push_cz(2, 0).push_swap(3, 1).push_cz(3, 2).build()
    code = generator.generate(graph)

    assert (
        code
        == """
from qiskit import QuantumCircuit

circuit = QuantumCircuit(4)
circuit.swap(0, 1)
circuit.cz(0, 2)
circuit.swap(1, 3)
circuit.cz(2, 3)
""".strip()
    )


def test_generate_circuit_with_three_qubits():
    graph = GraphBuilder().push_ccx(0, 2, 1).push_cswap(1, 0, 2).push_ccz(0, 1, 2).build()
    code = generator.generate(graph)

    assert (
        code
        == """
from qiskit import QuantumCircuit

circuit = QuantumCircuit(3)
circuit.ccx(0, 2, 1)
circuit.cswap(1, 0, 2)
circuit.ccz(0, 1, 2)
""".strip()
    )


def test_generate_circuit_with_multiple_bits():
    graph = GraphBuilder().push_h(0).push_x(1).push_y(2).measure_all()
    code = generator.generate(graph)

    assert (
        code
        == """
from qiskit import QuantumCircuit

circuit = QuantumCircuit(3, 3)
circuit.h(0)
circuit.x(1)
circuit.y(2)
circuit.measure(0, 0)
circuit.measure(1, 1)
circuit.measure(2, 2)
""".strip()
    )


def test_generate_circuit_with_flipped_measurements():
    graph = (
        GraphBuilder()
        .push_h(0)
        .push_z(1)
        .push_t(2)
        .push_measure(0, 1)
        .push_measure(1, 2)
        .push_measure(2, 0)
        .build()
    )
    code = generator.generate(graph)

    assert (
        code
        == """
from qiskit import QuantumCircuit

circuit = QuantumCircuit(3, 3)
circuit.h(0)
circuit.z(1)
circuit.t(2)
circuit.measure(0, 1)
circuit.measure(1, 2)
circuit.measure(2, 0)
""".strip()
    )
