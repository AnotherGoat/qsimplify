import pytest

from qsimplify.model import GraphBuilder
from qsimplify.model.quantum_graph import QuantumGraph
from qsimplify.simplifier import Simplifier

simplifier = Simplifier()


def test_simplified_graph_is_new_instance():
    graph = QuantumGraph()
    simplified_graph = simplifier.simplify_graph(graph)

    assert simplified_graph is not graph


def test_simplify_wrong_number_of_iterations():
    graph = QuantumGraph()

    with pytest.raises(ValueError, match="Number of iterations must be greater than 0"):
        simplifier.simplify_graph(graph, iterations=0)

    with pytest.raises(ValueError, match="Number of iterations must be greater than 0"):
        simplifier.simplify_graph(graph, iterations=-1)


def test_remove_filler_and_identities():
    graph = GraphBuilder().push_id(0).push_id(1).push_cx(0, 1).push_id(0).push_id(1).build(False)

    simplified_graph = simplifier.simplify_graph(graph)
    expected = GraphBuilder().push_cx(0, 1).build()

    assert simplified_graph == expected


def test_remove_duplicate_hadamards():
    graph = GraphBuilder().push_h(0).push_h(0).push_h(0).build()

    simplified_graph = simplifier.simplify_graph(graph)

    expected = GraphBuilder().push_h(0).build()

    assert simplified_graph == expected
