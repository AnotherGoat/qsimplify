import numpy

from qsimplify.analyzer import matrix_calculator
from qsimplify.model import GraphBuilder, QuantumGraph


def test_empty_graph_matrix():
    graph = QuantumGraph()

    assert matrix_calculator.circuit_matrix(graph) == numpy.eye(1, dtype=complex)


def test_hadamard_matrix():
    graph = GraphBuilder().push_h(0).build()

    expected = (1 / numpy.sqrt(2)) * numpy.array([[1, 1], [1, -1]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_x_matrix():
    graph = GraphBuilder().push_x(0).build()

    expected = numpy.array([[0, 1], [1, 0]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_y_matrix():
    graph = GraphBuilder().push_y(0).build()

    expected = numpy.array([[0, -1j], [1j, 0]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_z_matrix():
    graph = GraphBuilder().push_z(0).build()

    expected = numpy.array([[1, 0], [0, -1]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_phase_matrix():
    graph = GraphBuilder().push_p(numpy.pi, 0).build()

    expected = numpy.array([[1, 0], [0, -1]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_rx_matrix():
    graph = GraphBuilder().push_rx(numpy.pi, 0).build()

    expected = numpy.array([[0, -1j], [-1j, 0]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_ry_matrix():
    graph = GraphBuilder().push_ry(numpy.pi, 0).build()

    expected = numpy.array([[0, -1], [1, 0]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_rz_matrix():
    graph = GraphBuilder().push_rz(numpy.pi, 0).build()

    expected = numpy.array([[-1j, 0], [0, 1j]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_s_matrix():
    graph = GraphBuilder().push_s(0).build()

    expected = numpy.array([[1, 0], [0, 1j]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_s_dagger_matrix():
    graph = GraphBuilder().push_sdg(0).build()

    expected = numpy.array([[1, 0], [0, -1j]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_sqrt_x_matrix():
    graph = GraphBuilder().push_sx(0).build()

    expected = 0.5 * numpy.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_sqrt_y_matrix():
    graph = GraphBuilder().push_sy(0).build()

    expected = 0.5 * numpy.array([[1 + 1j, -1 - 1j], [1 + 1j, 1 + 1j]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_t_matrix():
    graph = GraphBuilder().push_t(0).build()

    expected = numpy.array([[1, 0], [0, numpy.exp(1j * numpy.pi / 4)]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_t_dagger_matrix():
    graph = GraphBuilder().push_tdg(0).build()

    expected = numpy.array([[1, 0], [0, numpy.exp(-1j * numpy.pi / 4)]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_ignore_measure_matrix():
    graph = GraphBuilder().push_measure(0, 0).build()

    expected = numpy.eye(2, dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)

    graph2 = GraphBuilder().push_measure(0, 0).push_measure(1, 1).build()

    expected2 = numpy.eye(4, dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph2), expected2)


def test_swap_matrix():
    graph = GraphBuilder().push_swap(0, 1).build()

    expected = numpy.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_control_hadamard_matrix():
    graph = GraphBuilder().push_ch(0, 1).build()

    hadamard = (1 / numpy.sqrt(2)) * numpy.array([[1, 1], [1, -1]], dtype=complex)

    expected = numpy.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, hadamard[0, 0], hadamard[0, 1]],
            [0, 0, hadamard[1, 0], hadamard[1, 1]],
        ],
        dtype=complex,
    )

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_reverse_ch_matrix():
    graph = GraphBuilder().push_ch(1, 0).build()

    inverse_sqrt2 = 1 / numpy.sqrt(2)

    expected = numpy.array(
        [
            [1, 0, 0, 0],
            [0, inverse_sqrt2, 0, inverse_sqrt2],
            [0, 0, 1, 0],
            [0, inverse_sqrt2, 0, -inverse_sqrt2],
        ],
        dtype=complex,
    )

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_cx_matrix():
    graph = GraphBuilder().push_cx(0, 1).build()

    expected = numpy.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_reverse_cx_matrix():
    graph = GraphBuilder().push_cx(1, 0).build()

    expected = numpy.array(
        [
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
        ],
        dtype=complex,
    )

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_cy_matrix():
    graph = GraphBuilder().push_cy(0, 1).build()

    expected = numpy.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, -1j],
            [0, 0, 1j, 0],
        ],
        dtype=complex,
    )

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_reverse_cy_matrix():
    graph = GraphBuilder().push_cy(1, 0).build()

    expected = numpy.array(
        [
            [1, 0, 0, 0],
            [0, 0, 0, -1j],
            [0, 0, 1, 0],
            [0, 1j, 0, 0],
        ],
        dtype=complex,
    )

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_control_phase_matrix():
    graph = GraphBuilder().push_cp(numpy.pi, 0, 1).build()

    expected = numpy.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, -1],
        ],
        dtype=complex,
    )

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_reverse_cp_matrix():
    graph = GraphBuilder().push_cp(numpy.pi, 1, 0).build()

    expected = numpy.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, -1],
        ],
        dtype=complex,
    )

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_cz_matrix():
    graph = GraphBuilder().push_cz(0, 1).build()

    expected = numpy.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]], dtype=complex)

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_cswap_matrix():
    graph = GraphBuilder().push_cswap(0, 1, 2).build()

    expected = numpy.eye(8, dtype=complex)
    expected[6, 6] = 0
    expected[5, 5] = 0
    expected[6, 5] = 1
    expected[5, 6] = 1

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_ccx_matrix():
    graph = GraphBuilder().push_ccx(0, 1, 2).build()

    expected = numpy.eye(8, dtype=complex)
    expected[6, 6] = 0
    expected[7, 7] = 0
    expected[6, 7] = 1
    expected[7, 6] = 1

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_ccz_matrix():
    graph = GraphBuilder().push_ccz(0, 1, 2).build()

    expected = numpy.eye(8, dtype=complex)
    expected[7, 7] = -1

    assert numpy.allclose(matrix_calculator.circuit_matrix(graph), expected)


def test_equivalent_swap():
    graph = GraphBuilder().push_swap(0, 1).build()
    graph2 = GraphBuilder().push_swap(1, 0).build()

    assert matrix_calculator.are_graphs_equivalent(graph, graph2)


def test_equivalent_cz():
    graph = GraphBuilder().push_cz(0, 1).build()
    graph2 = GraphBuilder().push_cz(1, 0).build()

    assert matrix_calculator.are_graphs_equivalent(graph, graph2)


def test_equivalent_cswap():
    graph = GraphBuilder().push_cswap(0, 1, 2).build()
    graph2 = GraphBuilder().push_cswap(0, 2, 1).build()

    assert matrix_calculator.are_graphs_equivalent(graph, graph2)


def test_equivalent_ccx():
    graph = GraphBuilder().push_ccx(0, 1, 2).build()
    graph2 = GraphBuilder().push_ccx(1, 0, 2).build()

    assert matrix_calculator.are_graphs_equivalent(graph, graph2)


def test_equivalent_ccz():
    graph = GraphBuilder().push_ccz(0, 1, 2).build()
    graph2 = GraphBuilder().push_ccz(0, 2, 1).build()
    graph3 = GraphBuilder().push_ccz(1, 0, 2).build()
    graph4 = GraphBuilder().push_ccz(1, 2, 0).build()
    graph5 = GraphBuilder().push_ccz(2, 0, 1).build()
    graph6 = GraphBuilder().push_ccz(2, 1, 0).build()

    assert matrix_calculator.are_graphs_equivalent(graph, graph2)
    assert matrix_calculator.are_graphs_equivalent(graph, graph3)
    assert matrix_calculator.are_graphs_equivalent(graph, graph4)
    assert matrix_calculator.are_graphs_equivalent(graph, graph5)
    assert matrix_calculator.are_graphs_equivalent(graph, graph6)

    assert matrix_calculator.are_graphs_equivalent(graph2, graph3)
    assert matrix_calculator.are_graphs_equivalent(graph2, graph4)
    assert matrix_calculator.are_graphs_equivalent(graph2, graph5)
    assert matrix_calculator.are_graphs_equivalent(graph2, graph6)

    assert matrix_calculator.are_graphs_equivalent(graph3, graph4)
    assert matrix_calculator.are_graphs_equivalent(graph3, graph5)
    assert matrix_calculator.are_graphs_equivalent(graph3, graph6)

    assert matrix_calculator.are_graphs_equivalent(graph4, graph5)
    assert matrix_calculator.are_graphs_equivalent(graph4, graph6)

    assert matrix_calculator.are_graphs_equivalent(graph5, graph6)
