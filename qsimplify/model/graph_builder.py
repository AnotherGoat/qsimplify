from __future__ import annotations

from qsimplify.model import graph_cleaner
from qsimplify.model.edge_name import EdgeName
from qsimplify.model.gate_name import GateName
from qsimplify.model.position import Position
from qsimplify.model.quantum_graph import QuantumGraph


class GraphBuilder:
    def __init__(self) -> None:
        self._graph = QuantumGraph()

    def __str__(self) -> str:
        return str(self._graph)

    def push_id(self, qubit: int) -> GraphBuilder:
        return self.put_id(qubit, self._find_push_column([qubit]))

    def push_h(self, qubit: int) -> GraphBuilder:
        return self.put_h(qubit, self._find_push_column([qubit]))

    def push_x(self, qubit: int) -> GraphBuilder:
        return self.put_x(qubit, self._find_push_column([qubit]))

    def push_y(self, qubit: int) -> GraphBuilder:
        return self.put_y(qubit, self._find_push_column([qubit]))

    def push_z(self, qubit: int) -> GraphBuilder:
        return self.put_z(qubit, self._find_push_column([qubit]))

    def push_rx(self, phi: float, qubit: int) -> GraphBuilder:
        return self.put_rx(phi, qubit, self._find_push_column([qubit]))

    def push_ry(self, theta: float, qubit: int) -> GraphBuilder:
        return self.put_ry(theta, qubit, self._find_push_column([qubit]))

    def push_rz(self, theta: float, qubit: int) -> GraphBuilder:
        return self.put_rz(theta, qubit, self._find_push_column([qubit]))

    def push_measure(self, qubit: int, bit: int) -> GraphBuilder:
        return self.put_measure(qubit, bit, self._find_push_column([qubit]))

    def push_swap(self, qubit1: int, qubit2: int) -> GraphBuilder:
        return self.put_swap(qubit1, qubit2, self._find_push_column([qubit1, qubit2]))

    def push_ch(self, control_qubit: int, target_qubit: int) -> GraphBuilder:
        return self.put_ch(
            control_qubit, target_qubit, self._find_push_column([control_qubit, target_qubit])
        )

    def push_cx(self, control_qubit: int, target_qubit: int) -> GraphBuilder:
        return self.put_cx(
            control_qubit, target_qubit, self._find_push_column([control_qubit, target_qubit])
        )

    def push_cz(self, qubit1: int, qubit2: int) -> GraphBuilder:
        return self.put_cz(qubit1, qubit2, self._find_push_column([qubit1, qubit2]))

    def push_cswap(
        self, control_qubit: int, target_qubit1: int, target_qubit2: int
    ) -> GraphBuilder:
        return self.put_cswap(
            control_qubit,
            target_qubit1,
            target_qubit2,
            self._find_push_column([control_qubit, target_qubit1, target_qubit2]),
        )

    def push_ccx(self, control_qubit1: int, control_qubit2: int, target_qubit: int) -> GraphBuilder:
        return self.put_ccx(
            control_qubit1,
            control_qubit2,
            target_qubit,
            self._find_push_column([control_qubit1, control_qubit2, target_qubit]),
        )

    def put_id(self, qubit: int, column: int) -> GraphBuilder:
        return self._put_single(GateName.ID, qubit, column)

    def put_h(self, qubit: int, column: int) -> GraphBuilder:
        return self._put_single(GateName.H, qubit, column)

    def put_x(self, qubit: int, column: int) -> GraphBuilder:
        return self._put_single(GateName.X, qubit, column)

    def put_y(self, qubit: int, column: int) -> GraphBuilder:
        return self._put_single(GateName.Y, qubit, column)

    def put_z(self, qubit: int, column: int) -> GraphBuilder:
        return self._put_single(GateName.Z, qubit, column)

    def _put_single(self, name: GateName, qubit: int, column: int) -> GraphBuilder:
        self._graph.add_new_node(name, Position(qubit, column))
        return self

    def put_rx(self, phi: float, qubit: int, column: int) -> GraphBuilder:
        return self._put_rotation(GateName.RX, phi, qubit, column)

    def put_ry(self, theta: float, qubit: int, column: int) -> GraphBuilder:
        return self._put_rotation(GateName.RY, theta, qubit, column)

    def put_rz(self, theta: float, qubit: int, column: int) -> GraphBuilder:
        return self._put_rotation(GateName.RZ, theta, qubit, column)

    def _put_rotation(self, name: GateName, angle: float, qubit: int, column: int) -> GraphBuilder:
        self._graph.add_new_node(name, Position(qubit, column), rotation=angle)
        return self

    def put_measure(self, qubit: int, bit: int, column: int) -> GraphBuilder:
        self._graph.add_new_node(GateName.MEASURE, Position(qubit, column), measure_to=bit)
        return self

    def put_swap(self, qubit1: int, qubit2: int, column: int) -> GraphBuilder:
        first = Position(qubit1, column)
        second = Position(qubit2, column)

        self._graph.add_new_node(GateName.SWAP, first)
        self._graph.add_new_node(GateName.SWAP, second)

        self._graph.add_new_edge(EdgeName.SWAPS_WITH, first, second)
        self._graph.add_new_edge(EdgeName.SWAPS_WITH, second, first)
        return self

    def put_ch(self, control_qubit: int, target_qubit: int, column: int) -> GraphBuilder:
        return self._put_control(GateName.CH, control_qubit, target_qubit, column)

    def put_cx(self, control_qubit: int, target_qubit: int, column: int) -> GraphBuilder:
        return self._put_control(GateName.CX, control_qubit, target_qubit, column)

    def _put_control(
        self, name: GateName, control_qubit: int, target_qubit: int, column: int
    ) -> GraphBuilder:
        control = Position(control_qubit, column)
        target = Position(target_qubit, column)

        self._graph.add_new_node(name, control)
        self._graph.add_new_node(name, target)

        self._graph.add_new_edge(EdgeName.TARGETS, control, target)
        self._graph.add_new_edge(EdgeName.CONTROLLED_BY, target, control)
        return self

    def put_cz(self, qubit1: int, qubit2: int, column: int) -> GraphBuilder:
        first = Position(qubit1, column)
        second = Position(qubit2, column)

        self._graph.add_new_node(GateName.CZ, first)
        self._graph.add_new_node(GateName.CZ, second)

        self._graph.add_new_edge(EdgeName.WORKS_WITH, first, second)
        self._graph.add_new_edge(EdgeName.WORKS_WITH, second, first)
        return self

    def put_cswap(
        self, control_qubit: int, target_qubit1: int, target_qubit2: int, column: int
    ) -> GraphBuilder:
        control = Position(control_qubit, column)
        target1 = Position(target_qubit1, column)
        target2 = Position(target_qubit2, column)

        self._graph.add_new_node(GateName.CSWAP, control)
        self._graph.add_new_node(GateName.CSWAP, target1)
        self._graph.add_new_node(GateName.CSWAP, target2)

        self._graph.add_new_edge(EdgeName.TARGETS, control, target1)
        self._graph.add_new_edge(EdgeName.TARGETS, control, target2)
        self._graph.add_new_edge(EdgeName.CONTROLLED_BY, target1, control)
        self._graph.add_new_edge(EdgeName.SWAPS_WITH, target1, target2)
        self._graph.add_new_edge(EdgeName.CONTROLLED_BY, target2, control)
        self._graph.add_new_edge(EdgeName.SWAPS_WITH, target2, target1)
        return self

    def put_ccx(
        self, control_qubit1: int, control_qubit2: int, target_qubit: int, column: int
    ) -> GraphBuilder:
        control1 = Position(control_qubit1, column)
        control2 = Position(control_qubit2, column)
        target = Position(target_qubit, column)

        self._graph.add_new_node(GateName.CCX, control1)
        self._graph.add_new_node(GateName.CCX, control2)
        self._graph.add_new_node(GateName.CCX, target)

        self._graph.add_new_edge(EdgeName.TARGETS, control1, target)
        self._graph.add_new_edge(EdgeName.WORKS_WITH, control1, control2)
        self._graph.add_new_edge(EdgeName.TARGETS, control2, target)
        self._graph.add_new_edge(EdgeName.WORKS_WITH, control2, control1)
        self._graph.add_new_edge(EdgeName.CONTROLLED_BY, target, control1)
        self._graph.add_new_edge(EdgeName.CONTROLLED_BY, target, control2)
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
        """
        Build the graph to get a working result.
        By default, any empty rows and columns will be deleted, unless clean_up is set to False.
        """
        if clean_up:
            graph_cleaner.clean_and_fill(self._graph)
        else:
            graph_cleaner.fill(self._graph)

        return self._graph

    def measure_all(self) -> QuantumGraph:
        """
        Build the graph by cleaning it up and then adding a measure gate for every qubit.
        """
        graph_cleaner.clean_and_fill(self._graph)

        for row in range(self._graph.height):
            self.push_measure(row, row)

        return self._graph
