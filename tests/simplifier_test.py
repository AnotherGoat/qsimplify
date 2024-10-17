from qiskit import QuantumCircuit
from quantum_circuit_simplifier.converter import Converter
from quantum_circuit_simplifier.model import QuantumGraph, GraphNode, EdgeName, GateName
from quantum_circuit_simplifier.simplifier import Simplifier

converter = Converter()
simplifier = Simplifier(converter)
ID = GateName.ID
H = GateName.H
def test_simplified_graph_is_new_instance():
    circuit = QuantumCircuit(2)

    graph = converter.circuit_to_graph(circuit)
    simplified_graph = simplifier.simplify_graph(graph)

    assert simplified_graph is not graph

def test_remove_duplicate_hadamards_1():
    graph = QuantumGraph()

    graph.add_node(GraphNode(H, (0, 0)))
    graph.add_node(GraphNode(H, (0, 1)))
    graph.add_node(GraphNode(H, (0, 2)))
    graph.add_edge(EdgeName.RIGHT, (0, 0), (0, 1))
    graph.add_edge(EdgeName.RIGHT, (0, 1), (0, 2))
    graph.add_edge(EdgeName.LEFT, (0, 2), (0, 1))
    graph.add_edge(EdgeName.LEFT, (0, 1), (0, 0))

    simplified_graph = simplifier.simplify_graph(graph)
    expected_graph = QuantumGraph()

    expected_graph.add_node(GraphNode(ID, (0, 0)))
    expected_graph.add_node(GraphNode(ID, (0, 1)))
    expected_graph.add_node(GraphNode(H, (0, 2)))
    expected_graph.add_edge(EdgeName.RIGHT, (0, 0), (0, 1))
    expected_graph.add_edge(EdgeName.RIGHT, (0, 1), (0, 2))
    expected_graph.add_edge(EdgeName.LEFT, (0, 2), (0, 1))
    expected_graph.add_edge(EdgeName.LEFT, (0, 1), (0, 0))

    assert simplified_graph == expected_graph
