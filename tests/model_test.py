from quantum_circuit_simplifier.model import GridNode, QuantumGrid, QuantumGraph, GraphNode, EdgeName


def test_create_node():
    node = GridNode("a")

    assert node.name == "a"
    assert node.targets == []
    assert node.controlled_by == []


def test_create_cx():
    control_node = GridNode("cx", targets=[1])
    target_node = GridNode("cx", controlled_by=[0])

    assert control_node.name == "cx"
    assert control_node.targets == [1]
    assert control_node.controlled_by == []
    assert target_node.name == "cx"
    assert target_node.targets == []
    assert target_node.controlled_by == [0]


def test_create_empty_grid():
    grid = QuantumGrid.create_empty(4, 3)

    for node in grid:
        assert node == QuantumGrid.FILLER

    assert grid.width == 4
    assert grid.height == 3


def test_trim_right_side():
    data = [
        [GridNode("h"), GridNode("x"), GridNode("y"), QuantumGrid.FILLER],
        [GridNode("z"), GridNode("h"), GridNode("x"), QuantumGrid.FILLER],
        [GridNode("y"), GridNode("z"), GridNode("h"), QuantumGrid.FILLER],
    ]
    grid = QuantumGrid(data)

    trimmed_grid = grid.trim_right_side()

    assert trimmed_grid.data == [
        [GridNode("h"), GridNode("x"), GridNode("y")],
        [GridNode("z"), GridNode("h"), GridNode("x")],
        [GridNode("y"), GridNode("z"), GridNode("h")],
    ]


def test_is_occupied():
    data = [
        [QuantumGrid.FILLER, GridNode("x"), GridNode("y")],
        [GridNode("z"), QuantumGrid.FILLER, GridNode("x")],
        [GridNode("y"), GridNode("z"), QuantumGrid.FILLER],
    ]
    grid = QuantumGrid(data)

    assert grid.is_occupied(0, 1)
    assert grid.is_occupied(0, 2)
    assert grid.is_occupied(1, 0)
    assert grid.is_occupied(1, 2)
    assert grid.is_occupied(2, 0)
    assert grid.is_occupied(2, 1)


def test_is_not_occupied():
    grid = QuantumGrid.create_empty(3, 3)

    for row in range(3):
        for column in range(3):
            assert not grid.is_occupied(row, column)


def test_has_node_at():
    grid = QuantumGrid.create_empty(3, 3)

    for row in range(3):
        for column in range(3):
            assert grid.has_node_at(row, column)


def test_doesnt_have_node_at():
    grid = QuantumGrid.create_empty(3, 3)

    assert not grid.has_node_at(0, -1)
    assert not grid.has_node_at(-1, 0)
    assert not grid.has_node_at(-1, -1)
    assert not grid.has_node_at(0, 3)
    assert not grid.has_node_at(3, 0)
    assert not grid.has_node_at(3, 3)


def test_add_node():
    graph = QuantumGraph()

    graph.add_node(GraphNode("id", (0, 0)))

    assert graph[0, 0] == GraphNode("id", (0, 0))


def test_graph_width():
    graph = QuantumGraph()

    graph.add_node(GraphNode("x", (0, 0)))
    assert graph.width == 1

    graph.add_node(GraphNode("x", (0, 5)))
    assert graph.width == 6


def test_graph_height():
    graph = QuantumGraph()

    graph.add_node(GraphNode("x", (0, 0)))
    assert graph.height == 1

    graph.add_node(GraphNode("x", (5, 0)))
    assert graph.height == 6


def test_graph_equals():
    graph1 = QuantumGraph()

    graph1.add_node(GraphNode("x", (0, 0)))
    graph1.add_node(GraphNode("x", (0, 1)))
    graph1.add_edge(EdgeName.RIGHT, (0, 0), (0, 1))
    graph1.add_edge(EdgeName.LEFT, (0, 1), (0, 0))

    graph2 = QuantumGraph()

    graph2.add_node(GraphNode("x", (0, 0)))
    graph2.add_node(GraphNode("x", (0, 1)))
    graph2.add_edge(EdgeName.RIGHT, (0, 0), (0, 1))
    graph2.add_edge(EdgeName.LEFT, (0, 1), (0, 0))

    assert graph1 == graph2


def test_graph_not_equals():
    graph1 = QuantumGraph()

    graph1.add_node(GraphNode("x", (0, 0)))
    graph1.add_node(GraphNode("x", (0, 1)))
    graph1.add_edge(EdgeName.RIGHT, (0, 0), (0, 1))
    graph1.add_edge(EdgeName.LEFT, (0, 1), (0, 0))

    graph2 = QuantumGraph()

    graph2.add_node(GraphNode("x", (0, 0)))
    graph2.add_node(GraphNode("y", (0, 1)))
    graph2.add_edge(EdgeName.LEFT, (0, 0), (0, 1))
    graph2.add_edge(EdgeName.RIGHT, (0, 1), (0, 0))

    assert graph1 != graph2