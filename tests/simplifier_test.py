from qiskit import QuantumCircuit
from quantum_circuit_simplifier.converter import Converter
from quantum_circuit_simplifier.model import QuantumGraph, EdgeName, GateName
from quantum_circuit_simplifier.simplifier import Simplifier

converter = Converter()
simplifier = Simplifier(converter)
ID = GateName.ID
H = GateName.H
CX = GateName.CX
RIGHT = EdgeName.RIGHT
LEFT = EdgeName.LEFT
TARGETS = EdgeName.TARGETS
CONTROLLED_BY = EdgeName.CONTROLLED_BY

class TestSimplifier:
    @staticmethod
    def test_simplified_graph_is_new_instance():
        circuit = QuantumCircuit(2)

        graph = converter.circuit_to_graph(circuit)
        simplified_graph = simplifier.simplify_graph(graph)

        assert simplified_graph is not graph


    @staticmethod
    def test_remove_filler_and_identities():
        graph = QuantumGraph()

        graph.add_new_node(ID, (0, 0))
        graph.add_new_node(ID, (1, 0))
        graph.add_new_node(CX, (0, 1))
        graph.add_new_node(CX, (1, 1))
        graph.add_new_node(ID, (0, 2))
        graph.add_new_node(ID, (1, 2))
        graph.fill_positional_edges()
        graph.add_new_edge(TARGETS, (0, 1), (1, 1))
        graph.add_new_edge(CONTROLLED_BY, (1, 1), (0, 1))

        simplified_graph = simplifier.simplify_graph(graph)
        simplified_circuit = converter.graph_to_circuit(simplified_graph)

        expected_circuit = QuantumCircuit(2)
        expected_circuit.cx(0, 1)

        assert simplified_circuit == expected_circuit

    @staticmethod
    def test_remove_duplicate_hadamards():
        graph = QuantumGraph()

        graph.add_new_node(H, (0, 0))
        graph.add_new_node(H, (0, 1))
        graph.add_new_node(H, (0, 2))
        graph.fill_positional_edges()

        simplified_graph = simplifier.simplify_graph(graph)
        expected_graph = QuantumGraph()

        expected_graph.add_new_node(ID, (0, 0))
        expected_graph.add_new_node(ID, (0, 1))
        expected_graph.add_new_node(H, (0, 2))
        expected_graph.fill_positional_edges()

        assert simplified_graph == expected_graph
