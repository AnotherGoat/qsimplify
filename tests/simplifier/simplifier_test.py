from qiskit import QuantumCircuit

from qsimplify.converter import Converter
from qsimplify.model import GraphBuilder, Position
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
        GraphBuilder().add_id(0, 0).add_id(1, 0).add_cx(0, 1, 1).add_id(0, 2).add_id(1, 2).build()
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

    mappings = {Position(0, 1): Position(0, 0), Position(0, 2): Position(0, 1)}

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
    pattern = GraphBuilder().add_h(0, 0).add_h(0, 1).build()

    graph = GraphBuilder().add_h(0, 0).add_h(0, 1).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {position: position for position in [Position(0, 0), Position(0, 1)]}

    assert mappings == expected_mappings


def test_find_pattern_in_same_two_qubit_pattern():
    pattern = GraphBuilder().add_x(0, 0).add_y(1, 0).add_z(0, 1).add_h(1, 1).build()

    graph = GraphBuilder().add_x(0, 0).add_y(1, 0).add_z(0, 1).add_h(1, 1).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {
        position: position
        for position in [Position(0, 0), Position(0, 1), Position(1, 0), Position(1, 1)]
    }

    assert mappings == expected_mappings


def test_find_inverted_two_qubit_pattern():
    pattern = GraphBuilder().add_x(0, 0).add_y(1, 0).add_z(0, 1).add_h(1, 1).build()

    graph = GraphBuilder().add_y(0, 0).add_x(1, 0).add_h(0, 1).add_z(1, 1).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {
        Position(0, 0): Position(1, 0),
        Position(0, 1): Position(1, 1),
        Position(1, 0): Position(0, 0),
        Position(1, 1): Position(0, 1),
    }

    assert mappings == expected_mappings


def test_find_same_controlled_pattern():
    pattern = GraphBuilder().add_cx(0, 1, 0).build()

    graph = GraphBuilder().add_cx(0, 1, 0).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {position: position for position in [Position(0, 0), Position(1, 0)]}

    assert mappings == expected_mappings


def test_find_same_mixed_pattern():
    pattern = GraphBuilder().add_cx(0, 1, 0).add_h(0, 1).add_z(1, 1).add_cx(1, 0, 2).build()

    graph = GraphBuilder().add_cx(0, 1, 0).add_h(0, 1).add_z(1, 1).add_cx(1, 0, 2).build()

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
    pattern = GraphBuilder().add_cx(0, 1, 0).add_h(0, 1).add_cx(1, 0, 2).add_z(1, 3).build()

    graph = GraphBuilder().add_cx(0, 1, 0).add_h(0, 1).add_cx(1, 0, 2).add_z(1, 3).build()

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
    pattern = GraphBuilder().add_cx(0, 1, 0).add_h(0, 1).add_cx(1, 0, 2).add_z(1, 3).build()

    graph = GraphBuilder().add_cx(1, 0, 0).add_h(1, 1).add_cx(0, 1, 2).add_z(0, 3).build()

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
    pattern = GraphBuilder().add_h(0, 0).add_x(1, 0).add_cz(0, 1, 1).add_swap(1, 0, 2).build()

    graph = GraphBuilder().add_h(0, 0).add_x(1, 0).add_cz(1, 0, 1).add_swap(0, 1, 2).build()

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
    pattern = GraphBuilder().add_h(0, 0).add_x(1, 0).build()

    graph = GraphBuilder().add_h(0, 0).add_x(1, 0).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {position: position for position in [Position(0, 0), Position(1, 0)]}

    graph = GraphBuilder().add_h(1, 0).add_x(0, 0).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(0, 0): Position(1, 0), Position(1, 0): Position(0, 0)}

    graph = GraphBuilder().add_h(0, 0).add_x(2, 0).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(0, 0): Position(0, 0), Position(2, 0): Position(1, 0)}

    graph = GraphBuilder().add_h(2, 0).add_x(0, 0).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(0, 0): Position(1, 0), Position(2, 0): Position(0, 0)}

    graph = GraphBuilder().add_h(1, 0).add_x(2, 0).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(1, 0): Position(0, 0), Position(2, 0): Position(1, 0)}

    graph = GraphBuilder().add_h(2, 0).add_x(1, 0).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(1, 0): Position(1, 0), Position(2, 0): Position(0, 0)}


def test_find_same_with_parameters():
    pattern = GraphBuilder().add_rx(0.5, 0, 0).add_measure(0, 0, 1).build()

    graph = GraphBuilder().add_rx(0.5, 0, 0).add_measure(0, 0, 1).build()

    mappings = simplifier.find_pattern(graph, pattern)

    expected_mappings = {position: position for position in [Position(0, 0), Position(0, 1)]}

    assert mappings == expected_mappings


def test_find_fails_if_parameters_dont_match():
    pattern = GraphBuilder().add_rx(0.5, 0, 0).add_measure(0, 0, 1).build()

    graph = GraphBuilder().add_rx(0.25, 0, 0).add_measure(0, 0, 1).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings is None

    graph = GraphBuilder().add_rx(0.5, 0, 0).add_measure(0, 1, 1).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings is None


def test_find_on_second_column():
    pattern = GraphBuilder().add_x(0, 0).add_z(0, 1).build()

    graph = GraphBuilder().add_h(0, 0).add_x(0, 1).add_z(0, 2).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {Position(0, 1): Position(0, 0), Position(0, 2): Position(0, 1)}


def test_find_uneven():
    pattern = GraphBuilder().add_x(0, 0).add_y(0, 1).add_z(1, 0).add_h(1, 1).build()

    graph = GraphBuilder().add_x(0, 0).add_y(0, 1).add_z(1, 1).add_h(1, 2).build()
    mappings = simplifier.find_pattern(graph, pattern)
    assert mappings == {
        Position(0, 0): Position(0, 0),
        Position(0, 1): Position(0, 1),
        Position(1, 1): Position(1, 0),
        Position(1, 2): Position(1, 1),
    }


def test_replace_single_qubit_gates():
    replacement = GraphBuilder().add_x(0, 0).add_y(1, 0).add_z(0, 1).build()

    graph = GraphBuilder().add_h(0, 0).add_h(0, 1).add_h(1, 0).add_h(1, 1).build()

    mappings = {
        Position(0, 0): Position(0, 1),
        Position(1, 0): Position(0, 0),
        Position(1, 1): Position(1, 0),
    }

    simplifier.replace_pattern(graph, replacement, mappings)
    expected_graph = GraphBuilder().add_z(0, 0).add_h(0, 1).add_x(1, 0).add_y(1, 1).build()

    assert graph == expected_graph


def test_replace_with_parameters():
    replacement = GraphBuilder().add_rx(0.25, 0, 0).add_ry(0.1, 1, 0).add_measure(0, 0, 1).build()

    graph = GraphBuilder().add_h(0, 0).add_h(0, 1).add_h(1, 0).add_h(1, 1).build()

    mappings = {
        Position(0, 0): Position(0, 1),
        Position(1, 0): Position(0, 0),
        Position(1, 1): Position(1, 0),
    }

    simplifier.replace_pattern(graph, replacement, mappings)
    expected_graph = (
        GraphBuilder().add_measure(0, 0, 0).add_h(0, 1).add_rx(0.25, 1, 0).add_ry(0.1, 1, 1).build()
    )

    assert graph == expected_graph


def test_replace_controlled_gates():
    replacement = GraphBuilder().add_cx(0, 1, 0).add_cx(1, 0, 1).build()

    graph = GraphBuilder().add_id(0, 0).add_id(0, 1).add_id(1, 0).add_id(1, 1).build()

    mappings = {
        Position(0, 0): Position(0, 1),
        Position(0, 1): Position(1, 0),
        Position(1, 0): Position(1, 1),
        Position(1, 1): Position(0, 0),
    }

    simplifier.replace_pattern(graph, replacement, mappings)
    expected_graph = GraphBuilder().add_cx(1, 0, 0).add_cx(1, 0, 1).build()

    assert graph == expected_graph


def test_replace_uneven():
    replacement = GraphBuilder().add_x(0, 0).add_y(0, 1).add_z(1, 0).add_x(1, 1).build()

    graph = (
        GraphBuilder()
        .add_h(0, 0)
        .add_h(0, 1)
        .add_h(0, 2)
        .add_h(1, 0)
        .add_h(1, 1)
        .add_h(1, 2)
        .build()
    )
    mappings = {
        Position(0, 0): Position(0, 0),
        Position(0, 1): Position(0, 1),
        Position(1, 1): Position(1, 0),
        Position(1, 2): Position(1, 1),
    }

    simplifier.replace_pattern(graph, replacement, mappings)
    expected_graph = (
        GraphBuilder()
        .add_x(0, 0)
        .add_y(0, 1)
        .add_h(0, 2)
        .add_h(1, 0)
        .add_z(1, 1)
        .add_x(1, 2)
        .build()
    )

    assert graph == expected_graph


def test_replace_adds_identities():
    replacement = GraphBuilder().add_cz(0, 1, 0).build()

    graph = (
        GraphBuilder()
        .add_y(0, 0)
        .add_y(0, 1)
        .add_z(1, 0)
        .add_h(1, 1)
        .add_cx(0, 1, 2)
        .add_z(0, 3)
        .add_h(1, 4)
        .build()
    )
    mappings = {
        Position(1, 1): None,
        Position(0, 2): Position(0, 0),
        Position(1, 2): Position(1, 0),
        Position(1, 4): None,
    }

    simplifier.replace_pattern(graph, replacement, mappings)
    expected_graph = (
        GraphBuilder().add_y(0, 0).add_y(0, 1).add_z(1, 0).add_cz(0, 1, 2).add_z(0, 3).build()
    )

    print(graph.draw_grid())
    print(expected_graph.draw_grid())

    assert graph == expected_graph
