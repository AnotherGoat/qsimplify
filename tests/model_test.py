from qsimplify.model import QuantumGraph, GraphNode, GraphEdge
from tests import *

class TestQuantumGraph:
    @staticmethod
    def test_add_node():
        graph = QuantumGraph()

        graph.add_new_node(ID, (0, 0))

        assert graph[0, 0] == GraphNode(ID, (0, 0))

    @staticmethod
    def test_graph_width():
        graph = QuantumGraph()

        graph.add_new_node(X, (0, 0))
        assert graph.width == 1

        graph.add_new_node(X, (0, 5))
        assert graph.width == 6

    @staticmethod
    def test_graph_height():
        graph = QuantumGraph()

        graph.add_new_node(X, (0, 0))
        assert graph.height == 1

        graph.add_new_node(X, (5, 0))
        assert graph.height == 6

    @staticmethod
    def test_empty_dimensions():
        graph = QuantumGraph()

        assert graph.width == 0
        assert graph.height == 0

    @staticmethod
    def test_graph_equals():
        graph1 = QuantumGraph()

        graph1.add_new_node(X, (0, 0))
        graph1.add_new_node(X, (0, 1))
        graph1.add_new_edge(EdgeName.RIGHT, (0, 0), (0, 1))
        graph1.add_new_edge(EdgeName.LEFT, (0, 1), (0, 0))

        graph2 = QuantumGraph()

        graph2.add_new_node(X, (0, 0))
        graph2.add_new_node(X, (0, 1))
        graph2.add_new_edge(EdgeName.RIGHT, (0, 0), (0, 1))
        graph2.add_new_edge(EdgeName.LEFT, (0, 1), (0, 0))

        assert graph1 == graph2

    @staticmethod
    def test_graph_not_equals():
        graph1 = QuantumGraph()

        graph1.add_new_node(X, (0, 0))
        graph1.add_new_node(X, (0, 1))
        graph1.add_new_edge(EdgeName.RIGHT, (0, 0), (0, 1))
        graph1.add_new_edge(EdgeName.LEFT, (0, 1), (0, 0))

        graph2 = QuantumGraph()

        graph2.add_new_node(X, (0, 0))
        graph2.add_new_node(Y, (0, 1))
        graph2.add_new_edge(EdgeName.LEFT, (0, 0), (0, 1))
        graph2.add_new_edge(EdgeName.RIGHT, (0, 1), (0, 0))

        assert graph1 != graph2

    @staticmethod
    def test_fill_positional_edges():
        graph = QuantumGraph()

        nodes = [
            GraphNode(ID, (0, 0)),
            GraphNode(ID, (0, 1)),
            GraphNode(ID, (1, 0)),
            GraphNode(ID, (1, 1)),
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

    @staticmethod
    def test_is_occupied():
        graph = QuantumGraph()

        graph.add_new_node(X, (0, 1))
        graph.add_new_node(Y, (0, 2))
        graph.add_new_node(Z, (1, 0))
        graph.add_new_node(X, (1, 2))
        graph.add_new_node(Y, (2, 0))
        graph.add_new_node(Z, (2, 1))
        graph.fill_empty_spaces()

        assert not graph.is_occupied(0, 0)
        assert graph.is_occupied(0, 1)
        assert graph.is_occupied(0, 2)
        assert graph.is_occupied(1, 0)
        assert not graph.is_occupied(1, 1)
        assert graph.is_occupied(1, 2)
        assert graph.is_occupied(2, 0)
        assert graph.is_occupied(2, 1)
        assert not graph.is_occupied(2, 2)

    @staticmethod
    def test_has_node_at():
        graph = QuantumGraph()

        graph.add_new_node(X, (0, 1))
        graph.add_new_node(Y, (0, 2))
        graph.add_new_node(Z, (1, 0))
        graph.add_new_node(X, (1, 2))
        graph.add_new_node(Y, (2, 0))
        graph.add_new_node(Z, (2, 1))

        assert not graph.has_node_at(0, 0)
        assert graph.has_node_at(0, 1)
        assert graph.has_node_at(0, 2)
        assert graph.has_node_at(1, 0)
        assert not graph.has_node_at(1, 1)
        assert graph.has_node_at(1, 2)
        assert graph.has_node_at(2, 0)
        assert graph.has_node_at(2, 1)
        assert not graph.has_node_at(2, 2)

    @staticmethod
    def test_doesnt_have_node_outside():
        graph = QuantumGraph()

        graph.add_new_node(H, (2, 2))
        graph.fill_empty_spaces()

        assert not graph.has_node_at(0, -1)
        assert not graph.has_node_at(-1, 0)
        assert not graph.has_node_at(-1, -1)
        assert not graph.has_node_at(0, 3)
        assert not graph.has_node_at(3, 0)
        assert not graph.has_node_at(3, 3)
