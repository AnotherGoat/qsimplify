from qsimplify.model import GraphBuilder, GraphEdge, GraphNode, Position, QuantumGraph
from tests import *


def test_add_node():
    graph = QuantumGraph()

    graph.add_new_node(ID, Position(0, 0))

    assert graph[Position(0, 0)] == GraphNode(ID, Position(0, 0))


def test_graph_width():
    graph = QuantumGraph()

    graph.add_new_node(X, Position(0, 0))
    assert graph.width == 1

    graph.add_new_node(X, Position(0, 5))
    assert graph.width == 6


def test_graph_height():
    graph = QuantumGraph()

    graph.add_new_node(X, Position(0, 0))
    assert graph.height == 1

    graph.add_new_node(X, Position(5, 0))
    assert graph.height == 6


def test_empty_dimensions():
    graph = QuantumGraph()

    assert graph.width == 0
    assert graph.height == 0


def test_fill_empty_spaces():
    graph = QuantumGraph()

    graph.add_new_node(H, Position(1, 1))
    graph.fill_empty_spaces()

    assert len(graph) == 4
    assert graph[Position(0, 0)].name == ID
    assert graph[Position(0, 1)].name == ID
    assert graph[Position(1, 0)].name == ID


def test_fill_positional_edges():
    graph = QuantumGraph()

    nodes = [
        GraphNode(ID, Position(0, 0)),
        GraphNode(ID, Position(0, 1)),
        GraphNode(ID, Position(1, 0)),
        GraphNode(ID, Position(1, 1)),
    ]

    for node in nodes:
        graph.add_node(node)

    graph.fill_positional_edges()
    edges = graph.edges()

    assert len(edges) == 4
    assert GraphEdge(RIGHT, nodes[0], nodes[1]) in edges
    assert GraphEdge(LEFT, nodes[1], nodes[0]) in edges
    assert GraphEdge(RIGHT, nodes[2], nodes[3]) in edges
    assert GraphEdge(LEFT, nodes[3], nodes[2]) in edges


def test_graph_equals():
    graph1 = GraphBuilder().add_x(0, 0).add_x(1, 1).build()
    graph2 = GraphBuilder().add_x(0, 0).add_x(1, 1).build()

    assert graph1 == graph2


def test_graph_not_equals():
    graph1 = GraphBuilder().add_x(0, 0).add_x(1, 1).build()
    graph2 = GraphBuilder().add_x(0, 0).add_y(1, 1).build()

    assert graph1 != graph2


def test_is_occupied():
    graph = (
        GraphBuilder()
        .add_x(0, 1)
        .add_y(0, 2)
        .add_z(1, 0)
        .add_x(1, 2)
        .add_y(2, 0)
        .add_z(2, 1)
        .build()
    )

    assert not graph.is_occupied(Position(0, 0))
    assert graph.is_occupied(Position(0, 1))
    assert graph.is_occupied(Position(0, 2))
    assert graph.is_occupied(Position(1, 0))
    assert not graph.is_occupied(Position(1, 1))
    assert graph.is_occupied(Position(1, 2))
    assert graph.is_occupied(Position(2, 0))
    assert graph.is_occupied(Position(2, 1))
    assert not graph.is_occupied(Position(2, 2))


def test_has_node_at():
    graph = QuantumGraph()

    graph.add_new_node(X, Position(0, 1))
    graph.add_new_node(Y, Position(0, 2))
    graph.add_new_node(Z, Position(1, 0))
    graph.add_new_node(X, Position(1, 2))
    graph.add_new_node(Y, Position(2, 0))
    graph.add_new_node(Z, Position(2, 1))

    assert not graph.has_node_at(Position(0, 0))
    assert graph.has_node_at(Position(0, 1))
    assert graph.has_node_at(Position(0, 2))
    assert graph.has_node_at(Position(1, 0))
    assert not graph.has_node_at(Position(1, 1))
    assert graph.has_node_at(Position(1, 2))
    assert graph.has_node_at(Position(2, 0))
    assert graph.has_node_at(Position(2, 1))
    assert not graph.has_node_at(Position(2, 2))


def test_doesnt_have_nodes_outside():
    graph = GraphBuilder().add_h(2, 2).build()

    assert not graph.has_node_at(Position(0, 3))
    assert not graph.has_node_at(Position(3, 0))
    assert not graph.has_node_at(Position(3, 3))
