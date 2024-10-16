from qiskit import QuantumCircuit

from quantum_circuit_simplifier.converter import Converter
from quantum_circuit_simplifier.model import GridNode, QuantumGrid

converter = Converter()

def test_empty_circuit_to_grid():
    circuit = QuantumCircuit(2)
    grid = converter.circuit_to_grid(circuit)

    assert grid.width == 0
    assert grid.height == 2


def test_one_qubit_to_grid():
    circuit = QuantumCircuit(1)

    circuit.h(0)
    circuit.x(0)
    circuit.y(0)
    circuit.z(0)
    circuit.x(0)
    circuit.z(0)
    circuit.h(0)
    circuit.y(0)

    grid = converter.circuit_to_grid(circuit)

    assert grid[0, 0] == GridNode("h")
    assert grid[0, 1] == GridNode("x")
    assert grid[0, 2] == GridNode("y")
    assert grid[0, 3] == GridNode("z")
    assert grid[0, 4] == GridNode("x")
    assert grid[0, 5] == GridNode("z")
    assert grid[0, 6] == GridNode("h")
    assert grid[0, 7] == GridNode("y")


def test_two_qubits_to_grid():
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.x(1)
    circuit.cx(0, 1)
    circuit.ch(1, 0)
    circuit.h(0)
    circuit.y(1)

    grid = converter.circuit_to_grid(circuit)

    assert grid[0, 0] == GridNode("h")
    assert grid[1, 0] == GridNode("x")

    assert grid[0, 1] == GridNode("cx", targets=[1])
    assert grid[1, 1] == GridNode("cx", controlled_by=[0])

    assert grid[0, 2] == GridNode("ch", controlled_by=[1])
    assert grid[1, 2] == GridNode("ch", targets=[0])

    assert grid[0, 3] == GridNode("h")
    assert grid[1, 3] == GridNode("y")


def test_entanglement_to_grid():
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.cx(0, 1)

    grid = converter.circuit_to_grid(circuit)

    assert grid[0, 0] == GridNode("h")
    assert grid[1, 0] == QuantumGrid.FILLER

    assert grid[0, 1] == GridNode("cx", targets=[1])
    assert grid[1, 1] == GridNode("cx", controlled_by=[0])


def test_three_qubits_to_grid():
    circuit = QuantumCircuit(3)

    circuit.cx(0, 1)
    circuit.cz(2, 1)
    circuit.ccx(0, 1, 2)
    circuit.h(2)

    grid = converter.circuit_to_grid(circuit)

    assert grid[0, 0] == GridNode("cx", targets=[1])
    assert grid[1, 0] == GridNode("cx", controlled_by=[0])
    assert grid[2, 0] == QuantumGrid.FILLER

    assert grid[0, 1] == QuantumGrid.FILLER
    assert grid[1, 1] == GridNode("cz", controlled_by=[2])
    assert grid[2, 1] == GridNode("cz", targets=[1])

    assert grid[0, 2] == GridNode("ccx", targets=[2])
    assert grid[1, 2] == GridNode("ccx", targets=[2])
    assert grid[2, 2] == GridNode("ccx", controlled_by=[0, 1])

    assert grid[0, 3] == QuantumGrid.FILLER
    assert grid[1, 3] == QuantumGrid.FILLER
    assert grid[2, 3] == GridNode("h")


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

    grid = converter.circuit_to_grid(circuit)

    assert grid.width == 7

    assert grid[0, 1] == GridNode("h")
    assert grid[0, 2] == GridNode("x")
    assert grid[1, 1] == GridNode("y")
    assert grid[1, 2] == QuantumGrid.FILLER
    assert grid[2, 0] == GridNode("z")
    assert grid[2, 1] == QuantumGrid.FILLER
    assert grid[2, 2] == QuantumGrid.FILLER

    assert grid[1, 3] == QuantumGrid.FILLER
    assert grid[2, 3] == QuantumGrid.FILLER
    assert grid[1, 4] == QuantumGrid.FILLER
    assert grid[2, 4] == QuantumGrid.FILLER

    assert grid[0, 6] == GridNode("x")
    assert grid[1, 6] == GridNode("y")
    assert grid[2, 6] == GridNode("z")


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

    assert graph[0, 0].name == "h"
    assert graph[0, 1].name == "x"
    assert graph[0, 2].name == "y"
    assert graph[0, 3].name == "z"
    assert graph[0, 4].name == "x"
    assert graph[0, 5].name == "z"
    assert graph[0, 6].name == "h"
    assert graph[0, 7].name == "y"


def test_horizontal_edges():
    circuit = QuantumCircuit(1)

    circuit.h(0)
    circuit.x(0)
    circuit.z(0)

    graph = converter.circuit_to_graph(circuit)

    edge_1 = graph.find_edges(0, 0)
    assert edge_1.left is None
    assert edge_1.right.name == "x"

    edge_2 = graph.find_edges(0, 1)
    assert edge_2.left.name == "h"
    assert edge_2.right.name == "z"

    edge_3 = graph.find_edges(0, 2)
    assert edge_3.left.name == "x"
    assert edge_3.right is None


def test_vertical_edges():
    circuit = QuantumCircuit(3)

    circuit.h(0)
    circuit.x(1)
    circuit.z(2)

    graph = converter.circuit_to_graph(circuit)

    h_edges = graph.find_edges(0, 0)
    assert h_edges.up is None
    assert h_edges.down.name == "x"

    x_edges = graph.find_edges(1, 0)
    assert x_edges.up.name == "h"
    assert x_edges.down.name == "z"

    z_edges = graph.find_edges(2, 0)
    assert z_edges.up.name == "x"
    assert z_edges.down is None


def test_control_edges():
    circuit = QuantumCircuit(3)

    circuit.cz(1, 0)
    circuit.swap(1, 2)
    circuit.ccx(1, 2, 0)
    circuit.cswap(0, 1, 2)

    graph = converter.circuit_to_graph(circuit)

    cz_edges_0 = graph.find_edges(0, 0)
    assert cz_edges_0.targets == []
    assert cz_edges_0.controlled_by[0].name == "cz"
    cz_edges_1 = graph.find_edges(1, 0)
    assert cz_edges_1.targets[0].name == "cz"
    assert cz_edges_1.controlled_by == []

    swap_edges_1 = graph.find_edges(1, 1)
    assert swap_edges_1.targets[0].name == "swap"
    assert swap_edges_1.controlled_by == []
    swap_edges_2 = graph.find_edges(2, 1)
    assert swap_edges_2.targets[0].name == "swap"
    assert swap_edges_2.controlled_by == []

    ccx_edges_0 = graph.find_edges(0, 2)
    assert ccx_edges_0.targets == []
    assert ccx_edges_0.controlled_by[0].name == "ccx"
    assert ccx_edges_0.controlled_by[1].name == "ccx"
    ccx_edges_1 = graph.find_edges(1, 2)
    assert ccx_edges_1.targets[0].name == "ccx"
    assert ccx_edges_1.controlled_by == []
    ccx_edges_2 = graph.find_edges(2, 2)
    assert ccx_edges_2.targets[0].name == "ccx"
    assert ccx_edges_2.controlled_by == []
    cswap_edges_0 = graph.find_edges(0, 3)
    assert cswap_edges_0.targets[0].name == "cswap"
    assert cswap_edges_0.targets[1].name == "cswap"
    assert cswap_edges_0.controlled_by == []
    cswap_edges_1 = graph.find_edges(1, 3)
    assert cswap_edges_1.targets == []
    assert cswap_edges_1.controlled_by[0].name == "cswap"
    cswap_edges_2 = graph.find_edges(2, 3)
    assert cswap_edges_2.targets == []
    assert cswap_edges_2.controlled_by[0].name == "cswap"


def test_one_qubit_graph_to_circuit():
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

    original_data = circuit.data
    converted_data = converted_circuit.data

    assert original_data == converted_data


def test_two_qubits_graph_to_circuit():
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

    original_data = circuit.data
    converted_data = converted_circuit.data

    assert original_data == converted_data
