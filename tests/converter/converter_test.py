from qiskit import QuantumCircuit

from qsimplify.converter import Converter
from qsimplify.model import GraphBuilder

converter = Converter()


def test_empty_circuit_to_graph():
    circuit = QuantumCircuit(2)
    graph = converter.circuit_to_graph(circuit)

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

    graph = converter.circuit_to_graph(circuit)

    expected = (
        GraphBuilder()
        .add_h(0, 0)
        .add_x(0, 1)
        .add_y(0, 2)
        .add_z(0, 3)
        .add_x(0, 4)
        .add_z(0, 5)
        .add_h(0, 6)
        .add_y(0, 7)
        .build()
    )

    print(graph)
    print(expected)

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

    graph = converter.circuit_to_graph(circuit)

    expected = (
        GraphBuilder()
        .add_h(0, 0)
        .add_x(1, 0)
        .add_y(0, 1)
        .add_z(1, 1)
        .add_x(0, 2)
        .add_z(1, 2)
        .add_h(0, 3)
        .add_y(1, 3)
        .build()
    )

    print(graph)
    print(expected)

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

    graph = converter.circuit_to_graph(circuit)

    expected = GraphBuilder().add_h(0, 0).add_y(0, 1).add_z(0, 2).add_x(0, 3).build()

    assert graph == expected


def test_skip_barriers():
    circuit = QuantumCircuit(3)

    circuit.x(2)
    circuit.barrier()
    circuit.z(0)
    circuit.barrier()
    circuit.y(1)

    graph = converter.circuit_to_graph(circuit)

    expected = GraphBuilder().add_z(0, 0).add_y(1, 0).add_x(2, 0).build()

    assert graph == expected


def test_rotation_nodes():
    circuit = QuantumCircuit(1)

    circuit.rx(0.75, 0)
    circuit.ry(0.5, 0)
    circuit.rz(0.25, 0)

    graph = converter.circuit_to_graph(circuit)

    expected = (
        GraphBuilder().add_rx(0.75, 0, 0).add_ry(0.5, 0, 1).add_rz(0.25, 0, 2).build()
    )

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

    graph = converter.circuit_to_graph(circuit)

    expected = (
        GraphBuilder()
        .add_h(0, 0)
        .add_measure(0, 2, 1)
        .add_h(1, 0)
        .add_h(1, 1)
        .add_measure(1, 1, 2)
        .add_h(2, 0)
        .add_measure(2, 0, 1)
        .build()
    )

    assert graph == expected


def test_control_edge_data():
    circuit = QuantumCircuit(3)

    circuit.cx(1, 0)
    circuit.ccx(1, 2, 0)

    graph = converter.circuit_to_graph(circuit)

    expected = GraphBuilder().add_cx(1, 0, 0).add_ccx(1, 2, 0, 1).build()

    print(graph)
    print(expected)

    assert graph == expected


def test_cz_edge_data():
    circuit = QuantumCircuit(3)

    circuit.cz(1, 0)

    graph = converter.circuit_to_graph(circuit)

    expected = GraphBuilder().add_cz(1, 0, 0).build()

    assert graph == expected


def test_swap_edge_data():
    circuit = QuantumCircuit(3)

    circuit.swap(1, 2)
    circuit.cswap(0, 1, 2)

    graph = converter.circuit_to_graph(circuit)

    expected = GraphBuilder().add_swap(1, 2, 0).add_cswap(0, 1, 2, 1).build()

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

    graph = converter.circuit_to_graph(circuit)

    expected = (
        GraphBuilder()
        .add_cx(0, 1, 0)
        .add_h(0, 1)
        .add_x(0, 2)
        .add_y(1, 1)
        .add_z(2, 0)
        .add_h(0, 3)
        .add_h(0, 4)
        .add_ccx(0, 1, 2, 5)
        .add_x(0, 6)
        .add_y(1, 6)
        .add_z(2, 6)
        .build()
    )

    assert graph == expected


def test_one_qubit_to_circuit():
    circuit = QuantumCircuit(1)

    circuit.h(0)
    circuit.x(0)
    circuit.y(0)
    circuit.z(0)
    circuit.x(0)
    circuit.z(0)
    circuit.h(0)
    circuit.y(0)

    graph = converter.circuit_to_graph(circuit)
    converted_circuit = converter.graph_to_circuit(graph)

    assert circuit.data == converted_circuit.data


def test_two_qubits_to_circuit():
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.x(1)
    circuit.cx(0, 1)
    circuit.ch(1, 0)
    circuit.cz(0, 1)
    circuit.y(0)
    circuit.z(1)

    graph = converter.circuit_to_graph(circuit)
    converted_circuit = converter.graph_to_circuit(graph)

    assert circuit.data == converted_circuit.data


def test_removed_identities():
    circuit = QuantumCircuit(5)

    circuit.id(0)
    circuit.id(1)
    circuit.id(2)

    graph = converter.circuit_to_graph(circuit)
    converted_circuit = converter.graph_to_circuit(graph)

    assert circuit.data != converted_circuit.data
    assert len(converted_circuit.data) == 0
