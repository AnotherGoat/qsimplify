import numpy

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
        graph.add_node(node.name, node.position, node.angle, node.bit)

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


def test_normalize_phase_angles():
    graph = QuantumGraph()

    graph.add_node(P, Position(0, 0), angle=0)
    graph.add_node(P, Position(0, 1), angle=numpy.pi)
    graph.add_node(P, Position(0, 2), angle=2 * numpy.pi)
    graph.add_node(P, Position(0, 3), angle=3 * numpy.pi)

    graph_cleaner.clean_and_fill(graph)

    assert len(graph) == 4
    assert graph[Position(0, 0)].angle == 0
    assert graph[Position(0, 1)].angle == numpy.pi
    assert graph[Position(0, 2)].angle == 0
    assert graph[Position(0, 3)].angle == numpy.pi


def test_normalize_rotation_angles():
    graph = QuantumGraph()

    graph.add_node(RX, Position(0, 0), angle=0)
    graph.add_node(RY, Position(0, 1), angle=numpy.pi)
    graph.add_node(RZ, Position(0, 2), angle=2 * numpy.pi)
    graph.add_node(RX, Position(0, 3), angle=3 * numpy.pi)
    graph.add_node(RY, Position(0, 4), angle=4 * numpy.pi)
    graph.add_node(RZ, Position(0, 5), angle=5 * numpy.pi)
    graph.add_node(RX, Position(0, 6), angle=50)

    graph_cleaner.clean_and_fill(graph)

    assert len(graph) == 7
    assert graph[Position(0, 0)].angle == 0
    assert graph[Position(0, 1)].angle == numpy.pi
    assert graph[Position(0, 2)].angle == 2 * numpy.pi
    assert graph[Position(0, 3)].angle == 3 * numpy.pi
    assert graph[Position(0, 4)].angle == 0
    assert graph[Position(0, 5)].angle == numpy.pi
    assert graph[Position(0, 6)].angle == 50 % (4 * numpy.pi)


def test_keep_cp_connections():
    graph = QuantumGraph()
    control = Position(0, 0)
    target = Position(1, 0)

    graph.add_node(CP, control)
    graph.add_node(CP, target, angle=3 * numpy.pi)
    graph.add_edge(EdgeName.TARGETS, control, target)
    graph.add_edge(EdgeName.CONTROLLED_BY, target, control)

    graph_cleaner.clean_and_fill(graph)

    assert len(graph) == 2
    assert graph[control].angle is None
    assert graph[target].angle == numpy.pi
    assert graph.edges() == [
        GraphEdge(EdgeName.TARGETS, graph[control], graph[target]),
        GraphEdge(EdgeName.CONTROLLED_BY, graph[target], graph[control]),
    ]


def test_remove_unused_bits():
    graph = QuantumGraph()

    graph.add_node(MEASURE, Position(0, 0), bit=0)
    graph.add_node(MEASURE, Position(1, 0), bit=1)
    graph.add_node(MEASURE, Position(2, 0), bit=3)

    assert graph.bits == 4

    graph_cleaner.clean_and_fill(graph)

    assert graph.bits == 3
