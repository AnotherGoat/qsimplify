from qiskit import QuantumCircuit

from qsimplify.model import GraphBuilder, Position
from qsimplify.model.quantum_graph import QuantumGraph
from qsimplify.simplifier import Simplifier

simplifier = Simplifier()


def test_simplified_graph_is_new_instance():
    graph = QuantumGraph()
    simplified_graph = simplifier.simplify_graph(graph)

    assert simplified_graph is not graph


def test_remove_filler_and_identities():
    graph = GraphBuilder().push_id(0).push_id(1).push_cx(0, 1).push_id(0).push_id(1).build(False)

    simplified_graph = simplifier.simplify_graph(graph)
    expected_graph = GraphBuilder().push_cx(0, 1).build()

    print(simplified_graph.draw_grid())
    print(expected_graph.draw_grid())

    assert simplified_graph == expected_graph


def test_remove_duplicate_hadamards():
    graph = GraphBuilder().push_h(0).push_h(0).push_h(0).build()

    simplified_graph = simplifier.simplify_graph(graph)

    expected = GraphBuilder().push_id(0).push_id(0).push_h(0).build()

    assert simplified_graph == expected


def test_replace_pattern():
    graph = GraphBuilder().push_x(0).push_h(0).push_h(0).build()

    replacement = GraphBuilder().push_y(0).push_y(0).build()

    mappings = {Position(0, 1): Position(0, 0), Position(0, 2): Position(0, 1)}

    expected = GraphBuilder().push_x(0).push_y(0).push_y(0).build()

    simplifier.replace_pattern(graph, replacement, mappings)

    assert graph == expected


def test_extract_subgraph_single_qubit():
    graph = GraphBuilder().push_x(0).push_h(0).push_z(0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 3)
    assert subgraph == graph

    first = GraphBuilder().push_x(0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 1)
    assert subgraph == first

    second = GraphBuilder().push_h(0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 1, 1)
    assert subgraph == second

    third = GraphBuilder().push_z(0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 2, 1)
    assert subgraph == third

    start = GraphBuilder().push_x(0).push_h(0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 2)
    assert subgraph == start

    end = GraphBuilder().push_h(0).push_z(0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 1, 2)
    assert subgraph == end


def test_extract_subgraph_two_qubits():
    graph = GraphBuilder().push_x(0).push_y(0).push_z(1).push_h(1).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0, 1], 0, 2)
    assert subgraph == graph

    first_row = GraphBuilder().push_x(0).push_y(0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 2)
    assert subgraph == first_row

    second_row = GraphBuilder().push_z(0).push_h(0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [1], 0, 2)
    assert subgraph == second_row

    first_column = GraphBuilder().push_x(0).push_z(1).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0, 1], 0, 1)
    assert subgraph == first_column

    second_column = GraphBuilder().push_y(0).push_h(1).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0, 1], 1, 1)
    assert subgraph == second_column


def test_extract_subgraph_keeps_data():
    graph = (
        GraphBuilder().push_rx(0.75, 0).push_ry(0.5, 0).push_rz(0.25, 0).push_measure(0, 3).build()
    )

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 4)
    assert subgraph == graph


def test_extract_subgraph_keeps_edges():
    graph = GraphBuilder().push_cswap(0, 1, 2).push_ccx(1, 2, 0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0, 1, 2], 0, 2)
    assert subgraph == graph


def test_extract_subgraph_in_other_order():
    graph = GraphBuilder().push_x(0).push_y(1).push_cx(2, 3).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [2, 1, 3, 0], 0, 1)

    expected = GraphBuilder().push_cx(0, 2).push_y(1).push_x(3).build()

    assert subgraph == expected


def test_extract_subgraph_skips_identities():
    graph = GraphBuilder().push_x(0).push_y(0).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 2)

    expected = GraphBuilder().push_x(0).push_y(0).build()

    assert subgraph == expected


def test_extract_subgraph_fails_outside():
    graph = GraphBuilder().put_y(0, 5).build(False)

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 2)
    assert subgraph is None


def test_extract_subgraph_doesnt_break_edges():
    graph = GraphBuilder().push_cx(0, 1).build()

    subgraph, _ = simplifier.extract_subgraph(graph, [0], 0, 1)
    assert subgraph is None

    subgraph, _ = simplifier.extract_subgraph(graph, [1], 0, 1)
    assert subgraph is None


def test_find_pattern_in_same_pattern():
    pattern = GraphBuilder().push_h(0).push_h(0).build()

    graph = GraphBuilder().push_h(0).push_h(0).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {position: position for position in [Position(0, 0), Position(0, 1)]}

    assert mappings == expected_mappings


def test_find_pattern_in_same_two_qubit_pattern():
    pattern = GraphBuilder().push_x(0).push_y(1).push_z(0).push_h(1).build()

    graph = GraphBuilder().push_x(0).push_y(1).push_z(0).push_h(1).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {
        position: position
        for position in [Position(0, 0), Position(0, 1), Position(1, 0), Position(1, 1)]
    }

    assert mappings == expected_mappings


def test_find_inverted_two_qubit_pattern():
    pattern = GraphBuilder().push_x(0).push_y(1).push_z(0).push_h(1).build()

    graph = GraphBuilder().push_y(0).push_x(1).push_h(0).push_z(1).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {
        Position(0, 0): Position(1, 0),
        Position(0, 1): Position(1, 1),
        Position(1, 0): Position(0, 0),
        Position(1, 1): Position(0, 1),
    }

    assert mappings == expected_mappings


def test_find_same_controlled_pattern():
    pattern = GraphBuilder().push_cx(0, 1).build()

    graph = GraphBuilder().push_cx(0, 1).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {position: position for position in [Position(0, 0), Position(1, 0)]}

    assert mappings == expected_mappings


def test_find_same_mixed_pattern():
    pattern = GraphBuilder().push_cx(0, 1).push_h(0).push_z(1).push_cx(1, 0).build()

    graph = GraphBuilder().push_cx(0, 1).push_h(0).push_z(1).push_cx(1, 0).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {
        position: position
        for position in [
            Position(0, 0),
            Position(0, 1),
            Position(0, 2),
            Position(1, 0),
            Position(1, 1),
            Position(1, 2),
        ]
    }

    assert mappings == expected_mappings


def test_find_same_mixed_pattern_with_mask():
    pattern = GraphBuilder().push_cx(0, 1).push_h(0).push_cx(1, 0).push_z(1).build()

    graph = GraphBuilder().push_cx(0, 1).push_h(0).push_cx(1, 0).push_z(1).build()

    mask = {
        Position(0, 0): True,
        Position(0, 1): True,
        Position(0, 2): True,
        Position(0, 3): False,
        Position(1, 0): True,
        Position(1, 1): False,
        Position(1, 2): True,
        Position(1, 3): True,
    }
    mappings = simplifier.find_pattern(graph, pattern, mask=mask)

    expected_mappings = {
        position: position
        for position in [
            Position(0, 0),
            Position(0, 1),
            Position(0, 2),
            Position(0, 3),
            Position(1, 0),
            Position(1, 1),
            Position(1, 2),
            Position(1, 3),
        ]
    }

    assert mappings == expected_mappings


def test_find_inverted_pattern_with_mask():
    pattern = GraphBuilder().push_cx(0, 1).push_h(0).push_cx(1, 0).push_z(1).build()

    graph = GraphBuilder().push_cx(1, 0).push_h(1).push_cx(0, 1).push_z(0).build()

    mask = {
        Position(0, 0): True,
        Position(0, 1): True,
        Position(0, 2): True,
        Position(0, 3): False,
        Position(1, 0): True,
        Position(1, 1): False,
        Position(1, 2): True,
        Position(1, 3): True,
    }
    mappings = simplifier.find_pattern(graph, pattern, mask=mask)

    expected_mappings = {
        Position(0, 0): Position(1, 0),
        Position(0, 1): Position(1, 1),
        Position(0, 2): Position(1, 2),
        Position(0, 3): Position(1, 3),
        Position(1, 0): Position(0, 0),
        Position(1, 1): Position(0, 1),
        Position(1, 2): Position(0, 2),
        Position(1, 3): Position(0, 3),
    }

    assert mappings == expected_mappings


def test_find_symmetrical_mappings():
    pattern = GraphBuilder().push_h(0).push_x(1).push_cz(0, 1).push_swap(1, 0).build()

    graph = GraphBuilder().push_h(0).push_x(1).push_cz(1, 0).push_swap(0, 1).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {
        position: position
        for position in [
            Position(0, 0),
            Position(0, 1),
            Position(0, 2),
            Position(1, 0),
            Position(1, 1),
            Position(1, 2),
        ]
    }

    assert mappings == expected_mappings


def test_find_three_qubit_permutations():
    pattern = GraphBuilder().push_h(0).push_x(1).build()

    graph = GraphBuilder().push_h(0).push_x(1).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {position: position for position in [Position(0, 0), Position(1, 0)]}

    graph = GraphBuilder().push_h(1).push_x(0).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(0, 0): Position(1, 0), Position(1, 0): Position(0, 0)}

    graph = GraphBuilder().push_h(0).push_x(2).build(clean_up=False)
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(0, 0): Position(0, 0), Position(2, 0): Position(1, 0)}

    graph = GraphBuilder().push_h(2).push_x(0).build(clean_up=False)
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(0, 0): Position(1, 0), Position(2, 0): Position(0, 0)}

    graph = GraphBuilder().push_h(1).push_x(2).build(clean_up=False)
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(1, 0): Position(0, 0), Position(2, 0): Position(1, 0)}

    graph = GraphBuilder().push_h(2).push_x(1).build(clean_up=False)
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(1, 0): Position(1, 0), Position(2, 0): Position(0, 0)}


def test_find_same_with_parameters():
    pattern = GraphBuilder().push_rx(0.5, 0).push_measure(0, 0).build()

    graph = GraphBuilder().push_rx(0.5, 0).push_measure(0, 0).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {position: position for position in [Position(0, 0), Position(0, 1)]}

    assert mappings == expected_mappings


def test_find_fails_if_parameters_dont_match():
    pattern = GraphBuilder().push_rx(0.5, 0).push_ry(0.5, 0).build()

    graph = GraphBuilder().push_rx(0.25, 0).push_ry(0.5, 0).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings is None

    graph = GraphBuilder().push_rx(0.5, 0).push_ry(0.75, 0).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings is None


def test_find_on_second_column():
    pattern = GraphBuilder().push_x(0).push_z(0).build()

    graph = GraphBuilder().push_h(0).push_x(0).push_z(0).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(0, 1): Position(0, 0), Position(0, 2): Position(0, 1)}


def test_find_uneven():
    pattern = GraphBuilder().push_x(0).push_y(0).push_z(1).push_h(1).build()

    graph = GraphBuilder().push_x(0).push_y(0).put_z(1, 1).push_h(1).build()
    mappings = simplifier.find_pattern(graph, pattern)

    print(mappings)
    assert mappings == {
        Position(0, 0): Position(0, 0),
        Position(0, 1): Position(0, 1),
        Position(1, 1): Position(1, 0),
        Position(1, 2): Position(1, 1),
    }


def test_replace_single_qubit_gates():
    replacement = GraphBuilder().push_x(0).push_y(1).push_z(0).build()

    graph = GraphBuilder().push_h(0).push_h(0).push_h(1).push_h(1).build()

    mappings = {
        Position(0, 0): Position(0, 1),
        Position(1, 0): Position(0, 0),
        Position(1, 1): Position(1, 0),
    }

    simplifier.replace_pattern(graph, replacement, mappings)
    expected_graph = GraphBuilder().push_z(0).push_h(0).push_x(1).push_y(1).build()

    assert graph == expected_graph


def test_replace_with_parameters():
    replacement = GraphBuilder().push_rx(0.25, 0).push_ry(0.1, 1).push_measure(0, 0).build()

    graph = GraphBuilder().push_h(0).push_h(0).push_h(1).push_h(1).build()

    mappings = {
        Position(0, 0): Position(0, 1),
        Position(1, 0): Position(0, 0),
        Position(1, 1): Position(1, 0),
    }

    simplifier.replace_pattern(graph, replacement, mappings)
    expected_graph = (
        GraphBuilder().push_measure(0, 0).push_h(0).push_rx(0.25, 1).push_ry(0.1, 1).build()
    )

    assert graph == expected_graph


def test_replace_controlled_gates():
    replacement = GraphBuilder().push_cx(0, 1).push_cx(1, 0).build()

    graph = GraphBuilder().push_id(0).push_id(0).push_id(1).push_id(1).build()

    mappings = {
        Position(0, 0): Position(0, 1),
        Position(0, 1): Position(1, 0),
        Position(1, 0): Position(1, 1),
        Position(1, 1): Position(0, 0),
    }

    simplifier.replace_pattern(graph, replacement, mappings)
    expected_graph = GraphBuilder().push_cx(1, 0).push_cx(1, 0).build()

    assert graph == expected_graph


def test_replace_uneven():
    replacement = GraphBuilder().push_x(0).push_y(0).push_z(1).push_x(1).build()

    graph = GraphBuilder().push_h(0).push_h(0).push_h(0).push_h(1).push_h(1).push_h(1).build()
    mappings = {
        Position(0, 0): Position(0, 0),
        Position(0, 1): Position(0, 1),
        Position(1, 1): Position(1, 0),
        Position(1, 2): Position(1, 1),
    }

    simplifier.replace_pattern(graph, replacement, mappings)
    expected_graph = (
        GraphBuilder().push_x(0).push_y(0).push_h(0).push_h(1).push_z(1).push_x(1).build()
    )

    assert graph == expected_graph


def test_replace_adds_identities():
    replacement = GraphBuilder().push_cz(0, 1).build()

    graph = (
        GraphBuilder()
        .push_y(0)
        .push_y(0)
        .push_z(1)
        .push_h(1)
        .push_cx(0, 1)
        .push_z(0)
        .put_h(1, 4)
        .build()
    )

    print(graph)

    mappings = {
        Position(1, 1): None,
        Position(0, 2): Position(0, 0),
        Position(1, 2): Position(1, 0),
        Position(1, 4): None,
    }

    simplifier.replace_pattern(graph, replacement, mappings)
    expected_graph = GraphBuilder().push_y(0).push_y(0).push_z(1).push_cz(0, 1).push_z(0).build()

    assert graph == expected_graph
