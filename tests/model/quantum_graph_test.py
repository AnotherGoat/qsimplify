import pytest

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


def test_graph_equals():
    graph1 = GraphBuilder().push_x(0).push_x(1).build()
    graph2 = GraphBuilder().push_x(0).push_x(1).build()

    assert graph1 == graph2


def test_graph_not_equals():
    graph1 = GraphBuilder().push_x(0).push_x(1).build()
    graph2 = GraphBuilder().push_x(0).push_y(1).build()

    assert graph1 != graph2


def test_is_occupied():
    graph = GraphBuilder().put_x(0, 1).push_y(0).push_z(1).put_x(1, 2).push_y(2).push_z(2).build()

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
    graph = GraphBuilder().put_h(2, 2).build(False)

    assert not graph.has_node_at(Position(0, 3))
    assert not graph.has_node_at(Position(3, 0))
    assert not graph.has_node_at(Position(3, 3))


def test_move_nonexistent_node():
    graph = QuantumGraph()

    graph.add_new_node(X, Position(0, 1))
    graph.add_new_node(Y, Position(0, 2))

    with pytest.raises(ValueError, match="Node at position \\(0, 3\\) does not exist"):
        graph.move_node(Position(0, 3), Position(1, 3))


def test_null_move():
    graph = QuantumGraph()

    graph.add_new_node(H, Position(0, 0))

    with pytest.raises(
        ValueError, match="Start and end positions shouldn't be the same \\(0, 0\\)"
    ):
        graph.move_node(Position(0, 0), Position(0, 0))


def test_move_node():
    graph = QuantumGraph()

    graph.add_new_node(X, Position(0, 1))
    graph.add_new_node(Y, Position(0, 2))
    graph.add_new_node(Z, Position(0, 3))

    graph.move_node(Position(0, 1), Position(1, 1))

    assert not graph.has_node_at(Position(0, 1))
    assert graph[Position(1, 1)] == GraphNode(X, Position(1, 1))


def test_move_node_preserves_edges():
    graph = QuantumGraph()

    graph.add_new_node(H, Position(0, 1))
    graph.add_new_node(Y, Position(1, 1))
    graph.add_new_node(CX, Position(0, 0))
    graph.add_new_node(CX, Position(1, 0))

    graph.add_new_edge(RIGHT, Position(0, 0), Position(0, 1))
    graph.add_new_edge(LEFT, Position(0, 1), Position(0, 0))
    graph.add_new_edge(TARGETS, Position(0, 0), Position(1, 0))
    graph.add_new_edge(CONTROLLED_BY, Position(1, 0), Position(0, 0))

    graph.move_node(Position(0, 0), Position(4, 0))

    hadamard = GraphNode(H, Position(0, 1))
    cx_controller = GraphNode(CX, Position(4, 0))
    cx_target = GraphNode(CX, Position(1, 0))

    edges = graph.edges()
    assert GraphEdge(RIGHT, cx_controller, hadamard) in edges
    assert GraphEdge(LEFT, hadamard, cx_controller) in edges
    assert GraphEdge(TARGETS, cx_controller, cx_target) in edges
    assert GraphEdge(CONTROLLED_BY, cx_target, cx_controller) in edges


def test_insert_column_on_empty_graph():
    graph = QuantumGraph()

    with pytest.raises(ValueError, match="It's not possible to insert a column on an empty graph"):
        graph.insert_column(0)


def test_insert_out_of_range_column():
    graph = QuantumGraph()

    graph.add_new_node(X, Position(0, 0))
    graph.add_new_node(Y, Position(0, 1))

    with pytest.raises(ValueError, match="Column index -1 is out of bounds"):
        graph.insert_column(-1)

    with pytest.raises(ValueError, match="Column index 3 is out of bounds"):
        graph.insert_column(3)


def test_insert_column():
    graph = QuantumGraph()

    graph.add_new_node(H, Position(0, 0))
    graph.add_new_node(X, Position(0, 1))
    graph.add_new_node(Y, Position(0, 2))
    graph.insert_column(1)

    assert graph.width == 4
    assert graph.height == 1
    assert graph[Position(0, 1)] == GraphNode(ID, Position(0, 1))
    assert graph[Position(0, 2)] == GraphNode(X, Position(0, 2))
    assert graph[Position(0, 3)] == GraphNode(Y, Position(0, 3))


def test_insert_column_at_end():
    graph = QuantumGraph()

    graph.add_new_node(X, Position(0, 0))
    graph.add_new_node(Y, Position(0, 1))
    graph.add_new_node(Z, Position(0, 2))
    graph.insert_column(3)

    assert graph.width == 4
    assert graph.height == 1
    assert graph[Position(0, 3)] == GraphNode(ID, Position(0, 3))


def test_insert_column_at_empty_space():
    graph = QuantumGraph()

    graph.add_new_node(X, Position(0, 0))
    graph.add_new_node(Y, Position(0, 2))
    graph.insert_column(1)

    assert graph.width == 4
    assert graph.height == 1
    assert graph[Position(0, 1)] == GraphNode(ID, Position(0, 1))
    assert not graph.has_node_at(Position(0, 2))
    assert graph[Position(0, 3)] == GraphNode(Y, Position(0, 3))
