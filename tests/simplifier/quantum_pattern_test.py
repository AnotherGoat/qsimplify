import pytest

from qsimplify.model import Position
from qsimplify.model.graph_builder import GraphBuilder
from qsimplify.simplifier import QuantumPattern


def test_empty_pattern():
    graph = GraphBuilder().build()

    with pytest.raises(ValueError, match="Quantum pattern can't be empty"):
        QuantumPattern(graph)


def test_pattern_with_measurement():
    graph = GraphBuilder().push_h(0).measure_all()

    with pytest.raises(ValueError, match="Quantum pattern can't have measurement gates"):
        QuantumPattern(graph)


def test_find_start():
    graph = GraphBuilder().push_x(0).build()
    pattern = QuantumPattern(graph)

    assert pattern.start.position == Position(0, 0)

    graph = GraphBuilder().push_x(1).build(False)
    pattern = QuantumPattern(graph)

    assert pattern.start.position == Position(1, 0)

    graph = GraphBuilder().push_id(0).push_id(1).push_x(2).build(False)
    pattern = QuantumPattern(graph)

    assert pattern.start.position == Position(2, 0)
