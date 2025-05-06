import pytest
from qiskit import QuantumCircuit
from qiskit.circuit.library.standard_gates import YGate

from qsimplify.converter import QiskitConverter
from qsimplify.model import GraphBuilder

converter = QiskitConverter()


def test_empty_to_graph():
    circuit = QuantumCircuit(2)
    graph = converter.to_graph(circuit)

    assert graph.width == 0
    assert graph.height == 0


def test_one_qubit_nodes():
    circuit = QuantumCircuit(1)

    circuit.h(0)
    circuit.x(0)
    circuit.y(0)
    circuit.z(0)
    circuit.x(0)
    circuit.z(0)
    circuit.h(0)
    circuit.y(0)

    graph = converter.to_graph(circuit)

    expected = (
        GraphBuilder()
        .push_h(0)
        .push_x(0)
        .push_y(0)
        .push_z(0)
        .push_x(0)
        .push_z(0)
        .push_h(0)
        .push_y(0)
        .build()
    )

    assert graph == expected


def test_two_qubit_nodes():
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.x(1)
    circuit.y(0)
    circuit.z(1)
    circuit.x(0)
    circuit.z(1)
    circuit.h(0)
    circuit.y(1)

    graph = converter.to_graph(circuit)

    expected = (
        GraphBuilder()
        .push_h(0)
        .push_x(1)
        .push_y(0)
        .push_z(1)
        .push_x(0)
        .push_z(1)
        .push_h(0)
        .push_y(1)
        .build()
    )

    assert graph == expected


def test_skip_identity_nodes():
    circuit = QuantumCircuit(1)

    circuit.h(0)
    circuit.id(0)
    circuit.y(0)
    circuit.z(0)
    circuit.id(0)
    circuit.id(0)
    circuit.x(0)
    circuit.id(0)

    graph = converter.to_graph(circuit)

    expected = GraphBuilder().push_h(0).push_y(0).push_z(0).push_x(0).build()

    assert graph == expected


def test_skip_barriers():
    circuit = QuantumCircuit(3)

    circuit.x(2)
    circuit.barrier()
    circuit.z(0)
    circuit.barrier()
    circuit.y(1)

    graph = converter.to_graph(circuit)

    expected = GraphBuilder().push_z(0).push_y(1).push_x(2).build()

    assert graph == expected


def test_rotation_nodes():
    circuit = QuantumCircuit(1)

    circuit.rx(0.75, 0)
    circuit.ry(0.5, 0)
    circuit.rz(0.25, 0)

    graph = converter.to_graph(circuit)

    expected = GraphBuilder().push_rx(0.75, 0).push_ry(0.5, 0).push_rz(0.25, 0).build()

    assert graph == expected


def test_measurement_nodes():
    circuit = QuantumCircuit(3, 3)

    circuit.h(0)
    circuit.measure(0, 2)
    circuit.h(1)
    circuit.h(1)
    circuit.measure(1, 1)
    circuit.h(2)
    circuit.measure(2, 0)

    graph = converter.to_graph(circuit)

    expected = (
        GraphBuilder()
        .push_h(0)
        .push_measure(0, 2)
        .push_h(1)
        .push_h(1)
        .push_measure(1, 1)
        .push_h(2)
        .push_measure(2, 0)
        .build()
    )

    assert graph == expected


def test_control_edge_data():
    circuit = QuantumCircuit(3)

    circuit.cx(1, 0)
    circuit.ccx(1, 2, 0)

    graph = converter.to_graph(circuit)

    expected = GraphBuilder().push_cx(1, 0).push_ccx(1, 2, 0).build()

    assert graph == expected


def test_cz_edge_data():
    circuit = QuantumCircuit(3)

    circuit.cz(1, 0)

    graph = converter.to_graph(circuit)

    expected = GraphBuilder().push_cz(1, 0).build()

    assert graph == expected


def test_swap_edge_data():
    circuit = QuantumCircuit(3)

    circuit.swap(1, 2)
    circuit.cswap(0, 1, 2)

    graph = converter.to_graph(circuit)

    expected = GraphBuilder().push_swap(1, 2).push_cswap(0, 1, 2).build()

    assert graph == expected


def test_qubit_placement():
    circuit = QuantumCircuit(3)

    circuit.cx(0, 1)
    circuit.h(0)
    circuit.x(0)
    circuit.y(1)
    circuit.z(2)
    circuit.h(0)
    circuit.h(0)
    circuit.ccx(0, 1, 2)
    circuit.x(0)
    circuit.y(1)
    circuit.z(2)

    graph = converter.to_graph(circuit)

    expected = (
        GraphBuilder()
        .push_cx(0, 1)
        .push_h(0)
        .push_x(0)
        .push_y(1)
        .push_z(2)
        .push_h(0)
        .push_h(0)
        .push_ccx(0, 1, 2)
        .push_x(0)
        .push_y(1)
        .push_z(2)
        .build()
    )

    assert graph == expected


def test_add_sy_to_graph():
    circuit = QuantumCircuit(1)

    circuit.append(YGate().power(1 / 2), [0])

    graph = converter.to_graph(circuit)
    expected = GraphBuilder().push_sy(0).build()

    assert graph == expected


def test_add_unknown_unitary_to_graph():
    circuit = QuantumCircuit(1)

    circuit.append(YGate().power(1 / 3), [0])

    with pytest.raises(ValueError, match=r"Non-SY unitary gates are not supported"):
        converter.to_graph(circuit)


def test_one_qubit_from_graph():
    circuit = QuantumCircuit(1)

    circuit.h(0)
    circuit.x(0)
    circuit.y(0)
    circuit.z(0)
    circuit.x(0)
    circuit.z(0)
    circuit.h(0)
    circuit.y(0)

    graph = converter.to_graph(circuit)
    converted_circuit = converter.from_graph(graph)

    assert circuit.data == converted_circuit.data


def test_two_qubits_from_graph():
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.x(1)
    circuit.cx(0, 1)
    circuit.ch(1, 0)
    circuit.cz(0, 1)
    circuit.y(0)
    circuit.z(1)

    graph = converter.to_graph(circuit)
    converted_circuit = converter.from_graph(graph)

    assert circuit.data == converted_circuit.data


def test_removed_identities():
    circuit = QuantumCircuit(5)

    circuit.id(0)
    circuit.id(1)
    circuit.id(2)

    graph = converter.to_graph(circuit)
    converted_circuit = converter.from_graph(graph)

    assert circuit.data != converted_circuit.data
    assert len(converted_circuit.data) == 0


def test_add_sy_from_graph():
    graph = GraphBuilder().push_sy(0).build()
    circuit = converter.from_graph(graph)

    expected = QuantumCircuit(1)
    expected.append(YGate().power(1 / 2), [0])

    assert circuit == expected
