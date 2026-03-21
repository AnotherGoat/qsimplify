from qsimplify.model import GraphBuilder, Position
from qsimplify.simplifier import pattern_replacer


def test_replace_pattern():
    graph = GraphBuilder().push_x(0).push_h(0).push_h(0).build()

    replacement = GraphBuilder().push_y(0).push_y(0).build()

    match = {Position(0, 1): Position(0, 0), Position(0, 2): Position(0, 1)}

    expected = GraphBuilder().push_x(0).push_y(0).push_y(0).build()

    pattern_replacer.replace_pattern(graph, replacement, match)

    assert graph == expected


def test_replace_single_qubit_gates():
    replacement = GraphBuilder().push_x(0).push_y(1).push_z(0).build()

    graph = GraphBuilder().push_h(0).push_h(0).push_h(1).push_h(1).build()

    match = {
        Position(0, 0): Position(0, 1),
        Position(1, 0): Position(0, 0),
        Position(1, 1): Position(1, 0),
    }

    pattern_replacer.replace_pattern(graph, replacement, match)
    expected = GraphBuilder().push_z(0).push_h(0).push_x(1).push_y(1).build()

    assert graph == expected


def test_replace_with_parameters():
    replacement = GraphBuilder().push_rx(0.25, 0).push_ry(0.1, 1).push_p(0.55, 0).build()

    graph = GraphBuilder().push_h(0).push_h(0).push_h(1).push_h(1).build()

    match = {
        Position(0, 0): Position(0, 1),
        Position(1, 0): Position(0, 0),
        Position(1, 1): Position(1, 0),
    }

    pattern_replacer.replace_pattern(graph, replacement, match)
    expected = GraphBuilder().push_p(0.55, 0).push_h(0).push_rx(0.25, 1).push_ry(0.1, 1).build()

    assert graph == expected


def test_replace_controlled_gates():
    replacement = GraphBuilder().push_cx(0, 1).push_cx(1, 0).build()

    graph = GraphBuilder().push_id(0).push_id(0).push_id(1).push_id(1).build()

    match = {
        Position(0, 0): Position(0, 1),
        Position(0, 1): Position(1, 0),
        Position(1, 0): Position(1, 1),
        Position(1, 1): Position(0, 0),
    }

    pattern_replacer.replace_pattern(graph, replacement, match)
    expected = GraphBuilder().push_cx(1, 0).push_cx(1, 0).build()

    assert graph == expected


def test_replace_uneven():
    replacement = GraphBuilder().push_x(0).push_y(0).push_z(1).push_x(1).build()

    graph = GraphBuilder().push_h(0).push_h(0).push_h(0).push_h(1).push_h(1).push_h(1).build()
    match = {
        Position(0, 0): Position(0, 0),
        Position(0, 1): Position(0, 1),
        Position(1, 1): Position(1, 0),
        Position(1, 2): Position(1, 1),
    }

    pattern_replacer.replace_pattern(graph, replacement, match)
    expected = GraphBuilder().push_x(0).push_y(0).push_h(0).push_h(1).push_z(1).push_x(1).build()

    assert graph == expected


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

    match = {
        Position(1, 1): None,
        Position(0, 2): Position(0, 0),
        Position(1, 2): Position(1, 0),
        Position(1, 4): None,
    }

    pattern_replacer.replace_pattern(graph, replacement, match)
    expected = GraphBuilder().push_y(0).push_y(0).push_z(1).push_cz(0, 1).push_z(0).build()

    assert graph == expected
