from qiskit import QuantumCircuit
from qsimplify.converter import Converter
from qsimplify.model import QuantumGraph
from qsimplify.simplifier import Simplifier
from tests import *

converter = Converter()
simplifier = Simplifier(converter)

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
        graph.add_new_edge(TARGETS, (0, 1), (1, 1))
        graph.add_new_edge(CONTROLLED_BY, (1, 1), (0, 1))

        graph.add_new_node(ID, (0, 2))
        graph.add_new_node(ID, (1, 2))
        graph.fill_positional_edges()

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

    @staticmethod
    def test_replace_pattern():
        graph = QuantumGraph()
        graph.add_new_node(X, (0, 0))
        graph.add_new_node(H, (0, 1))
        graph.add_new_node(H, (0, 2))
        graph.fill_positional_edges()

        replacement = QuantumGraph()
        replacement.add_new_node(Y, (0, 0))
        replacement.add_new_node(Y, (0, 1))
        replacement.fill_positional_edges()

        mappings = {(0, 1): (0, 0), (0, 2): (0, 1)}

        expected_graph = QuantumGraph()
        expected_graph.add_new_node(X, (0, 0))
        expected_graph.add_new_node(Y, (0, 1))
        expected_graph.add_new_node(Y, (0, 2))
        expected_graph.fill_positional_edges()

        simplifier.replace_pattern(graph, replacement, mappings)

        assert graph == expected_graph

    @staticmethod
    def test_extract_subgraph_single_qubit():
        graph = QuantumGraph()
        graph.add_new_node(X, (0, 0))
        graph.add_new_node(H, (0, 1))
        graph.add_new_node(Z, (0, 2))
        graph.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0], 0, 3)
        assert subgraph == graph

        first = QuantumGraph()
        first.add_new_node(X, (0, 0))

        subgraph, mappings = simplifier.extract_subgraph(graph, [0], 0, 1)
        assert subgraph == first

        second = QuantumGraph()
        second.add_new_node(H, (0, 0))

        subgraph, mappings = simplifier.extract_subgraph(graph, [0], 1, 1)
        assert subgraph == second

        third = QuantumGraph()
        third.add_new_node(Z, (0, 0))

        subgraph, mappings = simplifier.extract_subgraph(graph, [0], 2, 1)
        assert subgraph == third

        start = QuantumGraph()
        start.add_new_node(X, (0, 0))
        start.add_new_node(H, (0, 1))
        start.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0], 0, 2)
        assert subgraph == start

        end = QuantumGraph()
        end.add_new_node(H, (0, 0))
        end.add_new_node(Z, (0, 1))
        end.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0], 1, 2)
        assert subgraph == end

    @staticmethod
    def test_extract_subgraph_two_qubits():
        graph = QuantumGraph()
        graph.add_new_node(X, (0, 0))
        graph.add_new_node(Y, (0, 1))
        graph.add_new_node(Z, (1, 0))
        graph.add_new_node(H, (1, 1))
        graph.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0, 1], 0, 2)
        assert subgraph == graph

        first_row = QuantumGraph()
        first_row.add_new_node(X, (0, 0))
        first_row.add_new_node(Y, (0, 1))
        first_row.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0], 0, 2)
        assert subgraph == first_row

        second_row = QuantumGraph()
        second_row.add_new_node(Z, (0, 0))
        second_row.add_new_node(H, (0, 1))
        second_row.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [1], 0, 2)
        assert subgraph == second_row

        first_column = QuantumGraph()
        first_column.add_new_node(X, (0, 0))
        first_column.add_new_node(Z, (1, 0))
        first_column.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0, 1], 0, 1)
        assert subgraph == first_column

        second_column = QuantumGraph()
        second_column.add_new_node(Y, (0, 0))
        second_column.add_new_node(H, (1, 0))
        second_column.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0, 1], 1, 1)
        assert subgraph == second_column

    @staticmethod
    def test_extract_subgraph_keeps_data():
        graph = QuantumGraph()
        graph.add_new_node(RX, (0, 0), rotation=0.75)
        graph.add_new_node(RY, (0, 1), rotation=0.5)
        graph.add_new_node(RZ, (0, 2), rotation=0.25)
        graph.add_new_node(MEASURE, (0, 3), measure_to=3)
        graph.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0], 0, 4)
        assert subgraph == graph

    @staticmethod
    def test_extract_subgraph_keeps_edges():
        graph = QuantumGraph()

        graph.add_new_node(CSWAP, (0, 0))
        graph.add_new_node(CSWAP, (1, 0))
        graph.add_new_node(CSWAP, (2, 0))
        graph.add_new_edge(TARGETS, (0, 0), (1, 0))
        graph.add_new_edge(TARGETS, (0, 0), (2, 0))
        graph.add_new_edge(CONTROLLED_BY, (1, 0), (0, 0))
        graph.add_new_edge(SWAPS_WITH, (1, 0), (2, 0))
        graph.add_new_edge(CONTROLLED_BY, (2, 0), (0, 0))
        graph.add_new_edge(SWAPS_WITH, (2, 0), (1, 0))

        graph.add_new_node(CCX, (0, 1))
        graph.add_new_node(CCX, (1, 1))
        graph.add_new_node(CCX, (2, 1))
        graph.add_new_edge(CONTROLLED_BY, (0, 1), (1, 1))
        graph.add_new_edge(CONTROLLED_BY, (0, 1), (2, 1))
        graph.add_new_edge(TARGETS, (1, 1), (0, 1))
        graph.add_new_edge(WORKS_WITH, (1, 1), (2, 1))
        graph.add_new_edge(TARGETS, (2, 1), (0, 1))
        graph.add_new_edge(WORKS_WITH, (2, 1), (1, 1))

        graph.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0, 1, 2], 0, 2)
        assert subgraph == graph

    @staticmethod
    def test_extract_subgraph_in_other_order():
        graph = QuantumGraph()
        graph.add_new_node(X, (0, 0))
        graph.add_new_node(Y, (1, 0))
        graph.add_new_node(CX, (2, 0))
        graph.add_new_node(CX, (3, 0))
        graph.add_new_edge(TARGETS, (2, 0), (3, 0))
        graph.add_new_edge(CONTROLLED_BY, (3, 0), (2, 0))
        graph.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [2, 1, 3, 0], 0, 1)

        expected = QuantumGraph()
        expected.add_new_node(CX, (0, 0))
        expected.add_new_node(Y, (1, 0))
        expected.add_new_node(CX, (2, 0))
        expected.add_new_node(X, (3, 0))
        expected.add_new_edge(TARGETS, (0, 0), (2, 0))
        expected.add_new_edge(CONTROLLED_BY, (2, 0), (0, 0))
        expected.fill_positional_edges()

        assert subgraph == expected

    @staticmethod
    def test_extract_subgraph_skips_identities():
        graph = QuantumGraph()
        graph.add_new_node(X, (0, 1))
        graph.add_new_node(Y, (0, 5))
        graph.fill_empty_spaces()
        graph.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0], 0, 2)

        expected = QuantumGraph()
        expected.add_new_node(X, (0, 0))
        expected.add_new_node(Y, (0, 1))
        expected.fill_positional_edges()

        assert subgraph == expected

    @staticmethod
    def test_extract_subgraph_fails_outside():
        graph = QuantumGraph()
        graph.add_new_node(Y, (0, 5))
        graph.fill_empty_spaces()
        graph.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0], 0, 2)
        assert subgraph is None

    @staticmethod
    def test_extract_subgraph_doesnt_break_edges():
        graph = QuantumGraph()
        graph.add_new_node(CX, (0, 0))
        graph.add_new_node(CX, (1, 0))
        graph.add_new_edge(TARGETS, (0, 0), (1, 0))
        graph.add_new_edge(CONTROLLED_BY, (1, 0), (0, 0))
        graph.fill_positional_edges()

        subgraph, mappings = simplifier.extract_subgraph(graph, [0], 0, 1)
        assert subgraph is None

        subgraph, mappings = simplifier.extract_subgraph(graph, [1], 0, 1)
        assert subgraph is None

    @staticmethod
    def test_find_pattern_in_same_pattern():
        graph = QuantumGraph()
        graph.add_new_node(H, (0, 0))
        graph.add_new_node(H, (0, 1))
        graph.fill_positional_edges()

        pattern = QuantumGraph()
        pattern.add_new_node(H, (0, 0))
        pattern.add_new_node(H, (0, 1))
        pattern.fill_positional_edges()

        mappings = simplifier.find_pattern(graph, pattern)

        expected_mappings = {(0, 0): (0, 0), (0, 1): (0, 1)}

        assert mappings == expected_mappings
