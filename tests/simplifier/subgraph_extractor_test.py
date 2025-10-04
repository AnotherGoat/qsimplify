from qsimplify.model import GraphBuilder
from qsimplify.simplifier import subgraph_extractor


def test_extract_subgraph_single_qubit():
    graph = GraphBuilder().push_x(0).push_h(0).push_z(0).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0], 0, 3)
    assert subgraph == graph

    first = GraphBuilder().push_x(0).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0], 0, 1)
    assert subgraph == first

    second = GraphBuilder().push_h(0).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0], 1, 1)
    assert subgraph == second

    third = GraphBuilder().push_z(0).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0], 2, 1)
    assert subgraph == third

    start = GraphBuilder().push_x(0).push_h(0).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0], 0, 2)
    assert subgraph == start

    end = GraphBuilder().push_h(0).push_z(0).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0], 1, 2)
    assert subgraph == end


def test_extract_subgraph_two_qubits():
    graph = GraphBuilder().push_x(0).push_y(0).push_z(1).push_h(1).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0, 1], 0, 2)
    assert subgraph == graph

    first_row = GraphBuilder().push_x(0).push_y(0).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0], 0, 2)
    assert subgraph == first_row

    second_row = GraphBuilder().push_z(0).push_h(0).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [1], 0, 2)
    assert subgraph == second_row

    first_column = GraphBuilder().push_x(0).push_z(1).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0, 1], 0, 1)
    assert subgraph == first_column

    second_column = GraphBuilder().push_y(0).push_h(1).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0, 1], 1, 1)
    assert subgraph == second_column


def test_extract_subgraph_keeps_data():
    graph = (
        GraphBuilder().push_rx(0.75, 0).push_ry(0.5, 0).push_rz(0.25, 0).push_measure(0, 3).build()
    )

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0], 0, 4)
    assert subgraph == graph


def test_extract_subgraph_keeps_edges():
    graph = GraphBuilder().push_cswap(0, 1, 2).push_ccx(1, 2, 0).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0, 1, 2], 0, 2)
    assert subgraph == graph


def test_extract_subgraph_in_other_order():
    graph = GraphBuilder().push_x(0).push_y(1).push_cx(2, 3).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [2, 1, 3, 0], 0, 1)

    expected = GraphBuilder().push_cx(0, 2).push_y(1).push_x(3).build()

    assert subgraph == expected


def test_extract_subgraph_skips_identities():
    graph = GraphBuilder().push_x(0).push_y(0).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0], 0, 2)

    expected = GraphBuilder().push_x(0).push_y(0).build()

    assert subgraph == expected


def test_extract_subgraph_fails_outside():
    graph = GraphBuilder().put_y(0, 5).build(False)

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0], 0, 2)
    assert subgraph is None


def test_extract_subgraph_doesnt_break_edges():
    graph = GraphBuilder().push_cx(0, 1).build()

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [0], 0, 1)
    assert subgraph is None

    subgraph, _ = subgraph_extractor.extract_subgraph(graph, [1], 0, 1)
    assert subgraph is None
