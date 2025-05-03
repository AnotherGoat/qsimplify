from qsimplify.model import GraphEdge, GraphNode, Position, QuantumGraph, graph_cleaner
from tests import *


def test_fill_empty_spaces():
    graph = QuantumGraph()

    graph.add_node(H, Position(0, 0))
    graph.add_node(H, Position(1, 1))
    graph_cleaner.fill(graph)

    assert len(graph) == 4
    assert graph[Position(0, 1)].name == ID
    assert graph[Position(1, 0)].name == ID


def test_fix_positional_edges():
    graph = QuantumGraph()

    nodes = [
        GraphNode(Z, Position(0, 0)),
        GraphNode(Z, Position(0, 1)),
        GraphNode(Z, Position(1, 0)),
        GraphNode(Z, Position(1, 1)),
    ]

    for node in nodes:
        graph.add_node(node.name, node.position, node.rotation, node.measure_to)

    graph_cleaner.fill(graph)
    edges = graph.edges()

    assert len(edges) == 4
    assert GraphEdge(RIGHT, nodes[0], nodes[1]) in edges
    assert GraphEdge(LEFT, nodes[1], nodes[0]) in edges
    assert GraphEdge(RIGHT, nodes[2], nodes[3]) in edges
    assert GraphEdge(LEFT, nodes[3], nodes[2]) in edges


def test_remove_empty_rows():
    graph = QuantumGraph()

    graph.add_node(X, Position(0, 0))
    graph.add_node(ID, Position(3, 0))
    graph.add_node(X, Position(5, 0))
    graph_cleaner.clean_and_fill(graph)

    assert graph.height == 2


def test_remove_empty_columns():
    graph = QuantumGraph()

    graph.add_node(X, Position(0, 0))
    graph.add_node(ID, Position(0, 3))
    graph.add_node(X, Position(0, 5))
    graph_cleaner.clean_and_fill(graph)

    assert graph.width == 2


def test_remove_unused_bits():
    graph = QuantumGraph()

    graph.add_node(MEASURE, Position(0, 0), measure_to=0)
    graph.add_node(MEASURE, Position(1, 0), measure_to=1)
    graph.add_node(MEASURE, Position(2, 0), measure_to=3)

    assert graph.bits == 4

    graph_cleaner.clean_and_fill(graph)

    assert graph.bits == 3
