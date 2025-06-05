from __future__ import annotations

from qsimplify.model import graph_cleaner
from qsimplify.model.edge_name import EdgeName
from qsimplify.model.gate_name import GateName
from qsimplify.model.position import Position
from qsimplify.model.quantum_graph import QuantumGraph


class GraphBuilder:
    """Provides an interface for easily building a quantum graph."""

    def __init__(self) -> None:
        """Create an empty graph builder."""
        self._graph = QuantumGraph()

    def __str__(self) -> str:
        """Get a string representation of the builder, as a list of nodes followed by a list of edges."""
        return str(self._graph)

    def push_id(self, qubit: int) -> GraphBuilder:
        """Push a ID gate at the end of the graph, which effectively does nothing."""
        return self.put_id(qubit, self._find_push_column([qubit]))

    def push_h(self, qubit: int) -> GraphBuilder:
        """Push a H gate at the end of the graph."""
        return self.put_h(qubit, self._find_push_column([qubit]))

    def push_x(self, qubit: int) -> GraphBuilder:
        """Push a X gate at the end of the graph."""
        return self.put_x(qubit, self._find_push_column([qubit]))

    def push_y(self, qubit: int) -> GraphBuilder:
        """Push a Y gate at the end of the graph."""
        return self.put_y(qubit, self._find_push_column([qubit]))

    def push_z(self, qubit: int) -> GraphBuilder:
        """Push a Z gate at the end of the graph."""
        return self.put_z(qubit, self._find_push_column([qubit]))

    def push_p(self, angle: float, qubit: int) -> GraphBuilder:
        """Push a P gate at the end of the graph."""
        return self.put_p(angle, qubit, self._find_push_column([qubit]))

    def push_rx(self, angle: float, qubit: int) -> GraphBuilder:
        """Push a RX gate at the end of the graph."""
        return self.put_rx(angle, qubit, self._find_push_column([qubit]))

    def push_ry(self, angle: float, qubit: int) -> GraphBuilder:
        """Push a RY gate at the end of the graph."""
        return self.put_ry(angle, qubit, self._find_push_column([qubit]))

    def push_rz(self, angle: float, qubit: int) -> GraphBuilder:
        """Push a RZ gate at the end of the graph."""
        return self.put_rz(angle, qubit, self._find_push_column([qubit]))

    def push_s(self, qubit: int) -> GraphBuilder:
        """Push a S gate at the end of the graph."""
        return self.put_s(qubit, self._find_push_column([qubit]))

    def push_sdg(self, qubit: int) -> GraphBuilder:
        """Push a SDG gate at the end of the graph."""
        return self.put_sdg(qubit, self._find_push_column([qubit]))

    def push_sx(self, qubit: int) -> GraphBuilder:
        """Push a SX gate at the end of the graph."""
        return self.put_sx(qubit, self._find_push_column([qubit]))

    def push_sy(self, qubit: int) -> GraphBuilder:
        """Push a SY gate at the end of the graph."""
        return self.put_sy(qubit, self._find_push_column([qubit]))

    def push_t(self, qubit: int) -> GraphBuilder:
        """Push a T gate at the end of the graph."""
        return self.put_t(qubit, self._find_push_column([qubit]))

    def push_tdg(self, qubit: int) -> GraphBuilder:
        """Push a TDG gate at the end of the graph."""
        return self.put_tdg(qubit, self._find_push_column([qubit]))

    def push_measure(self, qubit: int, bit: int) -> GraphBuilder:
        """Push a MEASURE gate at the end of the graph."""
        return self.put_measure(qubit, bit, self._find_push_column([qubit]))

    def push_swap(self, qubit: int, qubit2: int) -> GraphBuilder:
        """Push a SWAP gate at the end of the graph."""
        return self.put_swap(qubit, qubit2, self._find_push_column([qubit, qubit2]))

    def push_ch(self, control_qubit: int, target_qubit: int) -> GraphBuilder:
        """Push a CH gate at the end of the graph."""
        return self.put_ch(
            control_qubit, target_qubit, self._find_push_column([control_qubit, target_qubit])
        )

    def push_cx(self, control_qubit: int, target_qubit: int) -> GraphBuilder:
        """Push a CX gate at the end of the graph."""
        return self.put_cx(
            control_qubit, target_qubit, self._find_push_column([control_qubit, target_qubit])
        )

    def push_cy(self, control_qubit: int, target_qubit: int) -> GraphBuilder:
        """Push a CY gate at the end of the graph."""
        return self.put_cy(
            control_qubit, target_qubit, self._find_push_column([control_qubit, target_qubit])
        )

    def push_cz(self, qubit: int, qubit2: int) -> GraphBuilder:
        """Push a CZ gate at the end of the graph."""
        return self.put_cz(qubit, qubit2, self._find_push_column([qubit, qubit2]))

    def push_cp(self, angle: float, control_qubit: int, target_qubit: int) -> GraphBuilder:
        """Push a CP gate at the end of the graph."""
        return self.put_cp(
            angle,
            control_qubit,
            target_qubit,
            self._find_push_column([control_qubit, target_qubit]),
        )

    def push_cswap(self, control_qubit: int, target_qubit: int, target_qubit2: int) -> GraphBuilder:
        """Push a CSWAP gate at the end of the graph."""
        return self.put_cswap(
            control_qubit,
            target_qubit,
            target_qubit2,
            self._find_push_column([control_qubit, target_qubit, target_qubit2]),
        )

    def push_ccx(self, control_qubit: int, control_qubit2: int, target_qubit: int) -> GraphBuilder:
        """Push a CCX gate at the end of the graph."""
        return self.put_ccx(
            control_qubit,
            control_qubit2,
            target_qubit,
            self._find_push_column([control_qubit, control_qubit2, target_qubit]),
        )

    def push_ccz(self, qubit: int, qubit2: int, qubit3: int) -> GraphBuilder:
        """Push a CCZ gate at the end of the graph."""
        return self.put_ccz(qubit, qubit2, qubit3, self._find_push_column([qubit, qubit2, qubit3]))

    def put_id(self, qubit: int, column: int) -> GraphBuilder:
        """Put a ID gate directly into the graph, which may break it when used incorrectly."""
        return self._put_single(GateName.ID, qubit, column)

    def put_h(self, qubit: int, column: int) -> GraphBuilder:
        """Put a H gate directly into the graph, which may break it when used incorrectly."""
        return self._put_single(GateName.H, qubit, column)

    def put_x(self, qubit: int, column: int) -> GraphBuilder:
        """Put a X gate directly into the graph, which may break it when used incorrectly."""
        return self._put_single(GateName.X, qubit, column)

    def put_y(self, qubit: int, column: int) -> GraphBuilder:
        """Put a Y gate directly into the graph, which may break it when used incorrectly."""
        return self._put_single(GateName.Y, qubit, column)

    def put_z(self, qubit: int, column: int) -> GraphBuilder:
        """Put a Z gate directly into the graph, which may break it when used incorrectly."""
        return self._put_single(GateName.Z, qubit, column)

    def _put_single(self, name: GateName, qubit: int, column: int) -> GraphBuilder:
        self._graph.add_node(name, Position(qubit, column))
        return self

    def put_p(self, angle: float, qubit: int, column: int) -> GraphBuilder:
        """Put a P gate directly into the graph, which may break it when used incorrectly."""
        return self._put_rotation(GateName.P, angle, qubit, column)

    def put_rx(self, angle: float, qubit: int, column: int) -> GraphBuilder:
        """Put a RX gate directly into the graph, which may break it when used incorrectly."""
        return self._put_rotation(GateName.RX, angle, qubit, column)

    def put_ry(self, angle: float, qubit: int, column: int) -> GraphBuilder:
        """Put a RY gate directly into the graph, which may break it when used incorrectly."""
        return self._put_rotation(GateName.RY, angle, qubit, column)

    def put_rz(self, angle: float, qubit: int, column: int) -> GraphBuilder:
        """Put a RZ gate directly into the graph, which may break it when used incorrectly."""
        return self._put_rotation(GateName.RZ, angle, qubit, column)

    def _put_rotation(self, name: GateName, angle: float, qubit: int, column: int) -> GraphBuilder:
        self._graph.add_node(name, Position(qubit, column), angle=angle)
        return self

    def put_s(self, qubit: int, column: int) -> GraphBuilder:
        """Put a S gate directly into the graph, which may break it when used incorrectly."""
        return self._put_single(GateName.S, qubit, column)

    def put_sdg(self, qubit: int, column: int) -> GraphBuilder:
        """Put a SDG gate directly into the graph, which may break it when used incorrectly."""
        return self._put_single(GateName.SDG, qubit, column)

    def put_sx(self, qubit: int, column: int) -> GraphBuilder:
        """Put a SX gate directly into the graph, which may break it when used incorrectly."""
        return self._put_single(GateName.SX, qubit, column)

    def put_sy(self, qubit: int, column: int) -> GraphBuilder:
        """Put a SY gate directly into the graph, which may break it when used incorrectly."""
        return self._put_single(GateName.SY, qubit, column)

    def put_t(self, qubit: int, column: int) -> GraphBuilder:
        """Put a T gate directly into the graph, which may break it when used incorrectly."""
        return self._put_single(GateName.T, qubit, column)

    def put_tdg(self, qubit: int, column: int) -> GraphBuilder:
        """Put a TDG gate directly into the graph, which may break it when used incorrectly."""
        return self._put_single(GateName.TDG, qubit, column)

    def put_measure(self, qubit: int, bit: int, column: int) -> GraphBuilder:
        """Put a MEASURE gate directly into the graph, which may break it when used incorrectly."""
        self._graph.add_node(GateName.MEASURE, Position(qubit, column), bit=bit)
        return self

    def put_swap(self, qubit: int, qubit2: int, column: int) -> GraphBuilder:
        """Put a SWAP gate directly into the graph, which may break it when used incorrectly."""
        first = Position(qubit, column)
        second = Position(qubit2, column)

        self._graph.add_node(GateName.SWAP, first)
        self._graph.add_node(GateName.SWAP, second)

        self._graph.add_bidirectional_edge(EdgeName.SWAPS_WITH, first, second)
        return self

    def put_ch(self, control_qubit: int, target_qubit: int, column: int) -> GraphBuilder:
        """Put a CH gate directly into the graph, which may break it when used incorrectly."""
        return self._put_control(GateName.CH, control_qubit, target_qubit, column)

    def put_cx(self, control_qubit: int, target_qubit: int, column: int) -> GraphBuilder:
        """Put a CX gate directly into the graph, which may break it when used incorrectly."""
        return self._put_control(GateName.CX, control_qubit, target_qubit, column)

    def put_cy(self, control_qubit: int, target_qubit: int, column: int) -> GraphBuilder:
        """Put a CY gate directly into the graph, which may break it when used incorrectly."""
        return self._put_control(GateName.CY, control_qubit, target_qubit, column)

    def _put_control(
        self, name: GateName, control_qubit: int, target_qubit: int, column: int
    ) -> GraphBuilder:
        control = Position(control_qubit, column)
        target = Position(target_qubit, column)

        self._graph.add_node(name, control)
        self._graph.add_node(name, target)

        self._graph.add_edge(EdgeName.TARGETS, control, target)
        self._graph.add_edge(EdgeName.CONTROLLED_BY, target, control)
        return self

    def put_cz(self, qubit: int, qubit2: int, column: int) -> GraphBuilder:
        """Put a CZ gate directly into the graph, which may break it when used incorrectly."""
        first = Position(qubit, column)
        second = Position(qubit2, column)

        self._graph.add_node(GateName.CZ, first)
        self._graph.add_node(GateName.CZ, second)

        self._graph.add_bidirectional_edge(EdgeName.WORKS_WITH, first, second)
        return self

    def put_cp(
        self, angle: float, control_qubit: int, target_qubit: int, column: int
    ) -> GraphBuilder:
        """Put a CP gate directly into the graph, which may break it when used incorrectly."""
        control = Position(control_qubit, column)
        target = Position(target_qubit, column)

        self._graph.add_node(GateName.CP, control)
        self._graph.add_node(GateName.CP, target, angle=angle)

        self._graph.add_edge(EdgeName.TARGETS, control, target)
        self._graph.add_edge(EdgeName.CONTROLLED_BY, target, control)
        return self

    def put_cswap(
        self, control_qubit: int, target_qubit: int, target_qubit2: int, column: int
    ) -> GraphBuilder:
        """Put a CSWAP gate directly into the graph, which may break it when used incorrectly."""
        control = Position(control_qubit, column)
        target = Position(target_qubit, column)
        target2 = Position(target_qubit2, column)

        self._graph.add_node(GateName.CSWAP, control)
        self._graph.add_node(GateName.CSWAP, target)
        self._graph.add_node(GateName.CSWAP, target2)

        self._graph.add_edge(EdgeName.TARGETS, control, target)
        self._graph.add_edge(EdgeName.TARGETS, control, target2)
        self._graph.add_edge(EdgeName.CONTROLLED_BY, target, control)
        self._graph.add_edge(EdgeName.CONTROLLED_BY, target2, control)
        self._graph.add_bidirectional_edge(EdgeName.SWAPS_WITH, target, target2)
        return self

    def put_ccx(
        self, control_qubit: int, control_qubit2: int, target_qubit: int, column: int
    ) -> GraphBuilder:
        """Put a CCX gate directly into the graph, which may break it when used incorrectly."""
        control = Position(control_qubit, column)
        control2 = Position(control_qubit2, column)
        target = Position(target_qubit, column)

        self._graph.add_node(GateName.CCX, control)
        self._graph.add_node(GateName.CCX, control2)
        self._graph.add_node(GateName.CCX, target)

        self._graph.add_edge(EdgeName.TARGETS, control, target)
        self._graph.add_edge(EdgeName.TARGETS, control2, target)
        self._graph.add_bidirectional_edge(EdgeName.WORKS_WITH, control, control2)
        self._graph.add_edge(EdgeName.CONTROLLED_BY, target, control)
        self._graph.add_edge(EdgeName.CONTROLLED_BY, target, control2)
        return self

    def put_ccz(self, qubit: int, qubit2: int, qubit3: int, column: int) -> GraphBuilder:
        """Put a CCZ gate directly into the graph, which may break it when used incorrectly."""
        first = Position(qubit, column)
        second = Position(qubit2, column)
        third = Position(qubit3, column)

        self._graph.add_node(GateName.CCZ, first)
        self._graph.add_node(GateName.CCZ, second)
        self._graph.add_node(GateName.CCZ, third)

        self._graph.add_bidirectional_edge(EdgeName.WORKS_WITH, first, second)
        self._graph.add_bidirectional_edge(EdgeName.WORKS_WITH, first, third)
        self._graph.add_bidirectional_edge(EdgeName.WORKS_WITH, second, third)
        return self

    def _find_push_column(self, qubits: list[int]) -> int:
        latest_columns = []

        for row in qubits:
            for column in reversed(range(self._graph.width)):
                node = self._graph[Position(row, column)]

                if node is not None and node.name != GateName.ID:
                    latest_columns.append(column + 1)
                    break

        return max(latest_columns) if latest_columns else 0

    def build(self, clean_up: bool = True) -> QuantumGraph:
        """Build the graph to get a working result.

        By default, any empty rows and columns will be deleted, unless clean_up is set to False.
        """
        if clean_up:
            graph_cleaner.clean_and_fill(self._graph)
        else:
            graph_cleaner.fill(self._graph)

        return self._graph

    def measure_all(self) -> QuantumGraph:
        """Build the graph by cleaning it up and then adding a measure gate for every qubit."""
        graph_cleaner.clean_and_fill(self._graph)

        for row in range(self._graph.height):
            self.push_measure(row, row)

        return self._graph
