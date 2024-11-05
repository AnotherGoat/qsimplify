from qiskit import QuantumCircuit

from qsimplify.converter import Converter
from qsimplify.model import GraphBuilder
from qsimplify.simplifier import Simplifier

converter = Converter()
simplifier = Simplifier(converter)


def test_simplified_graph_is_new_instance():
    circuit = QuantumCircuit(2)

    graph = converter.circuit_to_graph(circuit)
    simplified_graph = simplifier.simplify_graph(graph)

    assert simplified_graph is not graph


def test_remove_filler_and_identities():
    graph = (
        GraphBuilder()
        .add_id(0, 0)
        .add_id(1, 0)
        .add_cx(0, 1, 1)
        .add_id(0, 2)
        .add_id(1, 2)
        .build()
    )

    simplified_graph = simplifier.simplify_graph(graph)
    simplified_circuit = converter.graph_to_circuit(simplified_graph)

    expected_circuit = QuantumCircuit(2)
    expected_circuit.cx(0, 1)

    assert simplified_circuit == expected_circuit


def test_remove_duplicate_hadamards():
    graph = GraphBuilder().add_h(0, 0).add_h(0, 1).add_h(0, 2).build()

    simplified_graph = simplifier.simplify_graph(graph)

    expected = GraphBuilder().add_id(0, 0).add_id(0, 1).add_h(0, 2).build()

    assert simplified_graph == expected


def test_replace_pattern():
    graph = GraphBuilder().add_x(0, 0).add_h(0, 1).add_h(0, 2).build()

    replacement = GraphBuilder().add_y(0, 0).add_y(0, 1).build()

    mappings = {(0, 1): (0, 0), (0, 2): (0, 1)}

    expected = GraphBuilder().add_x(0, 0).add_y(0, 1).add_y(0, 2).build()

    simplifier.replace_pattern(graph, replacement, mappings)

    assert graph == expected


def test_extract_subgraph_single_qubit():
    graph = GraphBuilder().add_x(0, 0).add_h(0, 1).add_z(0, 2).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 3)
    assert subgraph == graph

    first = GraphBuilder().add_x(0, 0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 1)
    assert subgraph == first

    second = GraphBuilder().add_h(0, 0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 1, 1)
    assert subgraph == second

    third = GraphBuilder().add_z(0, 0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 2, 1)
    assert subgraph == third

    start = GraphBuilder().add_x(0, 0).add_h(0, 1).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 2)
    assert subgraph == start

    end = GraphBuilder().add_h(0, 0).add_z(0, 1).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 1, 2)
    assert subgraph == end


def test_extract_subgraph_two_qubits():
    graph = GraphBuilder().add_x(0, 0).add_y(0, 1).add_z(1, 0).add_h(1, 1).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0, 1], 0, 2)
    assert subgraph == graph

    first_row = GraphBuilder().add_x(0, 0).add_y(0, 1).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 2)
    assert subgraph == first_row

    second_row = GraphBuilder().add_z(0, 0).add_h(0, 1).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [1], 0, 2)
    assert subgraph == second_row

    first_column = GraphBuilder().add_x(0, 0).add_z(1, 0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0, 1], 0, 1)
    assert subgraph == first_column

    second_column = GraphBuilder().add_y(0, 0).add_h(1, 0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0, 1], 1, 1)
    assert subgraph == second_column


def test_extract_subgraph_keeps_data():
    graph = (
        GraphBuilder()
        .add_rx(0.75, 0, 0)
        .add_ry(0.5, 0, 1)
        .add_rz(0.25, 0, 2)
        .add_measure(0, 3, 3)
        .build()
    )

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 4)
    assert subgraph == graph


def test_extract_subgraph_keeps_edges():
    graph = GraphBuilder().add_cswap(0, 1, 2, 0).add_ccx(1, 2, 0, 1).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0, 1, 2], 0, 2)
    assert subgraph == graph


def test_extract_subgraph_in_other_order():
    graph = GraphBuilder().add_x(0, 0).add_y(1, 0).add_cx(2, 3, 0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [2, 1, 3, 0], 0, 1)

    expected = GraphBuilder().add_cx(0, 2, 0).add_y(1, 0).add_x(3, 0).build()

    assert subgraph == expected


def test_extract_subgraph_skips_identities():
    graph = GraphBuilder().add_x(0, 1).add_y(0, 5).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 2)

    expected = GraphBuilder().add_x(0, 0).add_y(0, 1).build()

    assert subgraph == expected


def test_extract_subgraph_fails_outside():
    graph = GraphBuilder().add_y(0, 5).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 2)
    assert subgraph is None


def test_extract_subgraph_doesnt_break_edges():
    graph = GraphBuilder().add_cx(0, 1, 0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 1)
    assert subgraph is None

    subgraph, _ = simplifier.extract_subgraph(graph, [1], 0, 1)
    assert subgraph is None


def test_find_pattern_in_same_pattern():
    graph = GraphBuilder().add_h(0, 0).add_h(0, 1).build()

    pattern = GraphBuilder().add_h(0, 0).add_h(0, 1).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {(0, 0): (0, 0), (0, 1): (0, 1)}

    assert mappings == expected_mappings
