from qsimplify.model import GraphBuilder, Position
from qsimplify.simplifier import QuantumPattern, pattern_matcher
from qsimplify.simplifier.position_mask import PositionMask


def test_match_pattern_in_same_pattern():
    pattern = GraphBuilder().push_h(0).push_h(0).build()

    graph = GraphBuilder().push_h(0).push_h(0).build()

    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)

    expected = {position: position for position in [Position(0, 0), Position(0, 1)]}

    assert match == expected


def test_match_pattern_in_same_two_qubit_pattern():
    pattern = GraphBuilder().push_x(0).push_y(1).push_z(0).push_h(1).build()

    graph = GraphBuilder().push_x(0).push_y(1).push_z(0).push_h(1).build()

    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)

    expected = {
        position: position
        for position in [Position(0, 0), Position(0, 1), Position(1, 0), Position(1, 1)]
    }

    assert match == expected


def test_match_inverted_two_qubit_pattern():
    pattern = GraphBuilder().push_x(0).push_y(1).push_z(0).push_h(1).build()

    graph = GraphBuilder().push_y(0).push_x(1).push_h(0).push_z(1).build()

    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)

    expected = {
        Position(0, 0): Position(1, 0),
        Position(0, 1): Position(1, 1),
        Position(1, 0): Position(0, 0),
        Position(1, 1): Position(0, 1),
    }

    assert match == expected


def test_match_same_controlled_pattern():
    pattern = GraphBuilder().push_cx(0, 1).build()

    graph = GraphBuilder().push_cx(0, 1).build()

    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)

    expected = {position: position for position in [Position(0, 0), Position(1, 0)]}

    assert match == expected


def test_match_same_mixed_pattern():
    pattern = GraphBuilder().push_cx(0, 1).push_h(0).push_z(1).push_cx(1, 0).build()

    graph = GraphBuilder().push_cx(0, 1).push_h(0).push_z(1).push_cx(1, 0).build()

    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)

    expected = {
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

    assert match == expected


def test_match_same_mixed_pattern_with_mask():
    pattern = GraphBuilder().push_cx(0, 1).push_h(0).push_cx(1, 0).push_z(1).build()

    graph = GraphBuilder().push_cx(0, 1).push_h(0).push_cx(1, 0).push_z(1).build()

    mask = PositionMask(
        {
            Position(0, 0): True,
            Position(0, 1): True,
            Position(0, 2): True,
            Position(0, 3): False,
            Position(1, 0): True,
            Position(1, 1): False,
            Position(1, 2): True,
            Position(1, 3): True,
        }
    )
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph, mask=mask)

    expected = {
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

    assert match == expected


def test_match_inverted_pattern_with_mask():
    pattern = GraphBuilder().push_cx(0, 1).push_h(0).push_cx(1, 0).push_z(1).build()

    graph = GraphBuilder().push_cx(1, 0).push_h(1).push_cx(0, 1).push_z(0).build()

    mask = PositionMask(
        {
            Position(0, 0): True,
            Position(0, 1): True,
            Position(0, 2): True,
            Position(0, 3): False,
            Position(1, 0): True,
            Position(1, 1): False,
            Position(1, 2): True,
            Position(1, 3): True,
        }
    )
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph, mask=mask)

    expected = {
        Position(0, 0): Position(1, 0),
        Position(0, 1): Position(1, 1),
        Position(0, 2): Position(1, 2),
        Position(0, 3): Position(1, 3),
        Position(1, 0): Position(0, 0),
        Position(1, 1): Position(0, 1),
        Position(1, 2): Position(0, 2),
        Position(1, 3): Position(0, 3),
    }

    assert match == expected


def test_match_symmetrical_match():
    pattern = GraphBuilder().push_h(0).push_x(1).push_cz(0, 1).push_swap(1, 0).build()

    graph = GraphBuilder().push_h(0).push_x(1).push_cz(1, 0).push_swap(0, 1).build()

    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)

    expected = {
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

    assert match == expected


def test_match_three_qubit_permutations():
    pattern = GraphBuilder().push_h(0).push_x(1).build()

    graph = GraphBuilder().push_h(0).push_x(1).build()
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)
    assert match == {position: position for position in [Position(0, 0), Position(1, 0)]}

    graph = GraphBuilder().push_h(1).push_x(0).build()
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)
    assert match == {Position(0, 0): Position(1, 0), Position(1, 0): Position(0, 0)}

    graph = GraphBuilder().push_h(0).push_x(2).build(clean_up=False)
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)
    assert match == {Position(0, 0): Position(0, 0), Position(2, 0): Position(1, 0)}

    graph = GraphBuilder().push_h(2).push_x(0).build(clean_up=False)
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)
    assert match == {Position(0, 0): Position(1, 0), Position(2, 0): Position(0, 0)}

    graph = GraphBuilder().push_h(1).push_x(2).build(clean_up=False)
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)
    assert match == {Position(1, 0): Position(0, 0), Position(2, 0): Position(1, 0)}

    graph = GraphBuilder().push_h(2).push_x(1).build(clean_up=False)
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)
    assert match == {Position(1, 0): Position(1, 0), Position(2, 0): Position(0, 0)}


def test_match_same_with_parameters():
    pattern = GraphBuilder().push_rx(0.5, 0).push_p(0.75, 0).build()

    graph = GraphBuilder().push_rx(0.5, 0).push_p(0.75, 0).build()

    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)

    expected = {position: position for position in [Position(0, 0), Position(0, 1)]}

    assert match == expected


def test_match_fails_if_parameters_dont_match():
    pattern = GraphBuilder().push_rx(0.5, 0).push_ry(0.5, 0).build()

    graph = GraphBuilder().push_rx(0.25, 0).push_ry(0.5, 0).build()
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)
    assert match is None

    graph = GraphBuilder().push_rx(0.5, 0).push_ry(0.75, 0).build()
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)
    assert match is None


def test_match_on_second_column():
    pattern = GraphBuilder().push_x(0).push_z(0).build()

    graph = GraphBuilder().push_h(0).push_x(0).push_z(0).build()
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)
    assert match == {Position(0, 1): Position(0, 0), Position(0, 2): Position(0, 1)}


def test_match_uneven():
    pattern = GraphBuilder().push_x(0).push_y(0).push_z(1).push_h(1).build()

    graph = GraphBuilder().push_x(0).push_y(0).put_z(1, 1).push_h(1).build()
    match = pattern_matcher.match_pattern(QuantumPattern(pattern), graph)

    assert match == {
        Position(0, 0): Position(0, 0),
        Position(0, 1): Position(0, 1),
        Position(1, 1): Position(1, 0),
        Position(1, 2): Position(1, 1),
    }
