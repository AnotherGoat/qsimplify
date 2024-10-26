from __future__ import annotations

from qsimplify.model.quantum_graph import QuantumGraph
from qsimplify.model.gate_name import GateName
from qsimplify.model.edge_name import EdgeName

_SWAPS_WITH = EdgeName.SWAPS_WITH
_TARGETS = EdgeName.TARGETS
_CONTROLLED_BY = EdgeName.CONTROLLED_BY
_WORKS_WITH = EdgeName.WORKS_WITH

class GraphBuilder:
    def __init__(self):
        self._graph = QuantumGraph()

    def __str__(self) -> str:
        return str(self._graph)

    def is_occupied(self, row: int, column: int) -> bool:
        return self._graph.is_occupied(row, column)

    def add_id(self, qubit: int, column: int) -> GraphBuilder:
        return self.add_single(GateName.ID, qubit, column)

    def add_h(self, qubit: int, column: int) -> GraphBuilder:
        return self.add_single(GateName.H, qubit, column)

    def add_x(self, qubit: int, column: int) -> GraphBuilder:
        return self.add_single(GateName.X, qubit, column)

    def add_y(self, qubit: int, column: int) -> GraphBuilder:
        return self.add_single(GateName.Y, qubit, column)

    def add_z(self, qubit: int, column: int) -> GraphBuilder:
        return self.add_single(GateName.Z, qubit, column)

    def add_single(self, name: GateName, qubit: int, column: int) -> GraphBuilder:
        if name not in (GateName.ID, GateName.H, GateName.X, GateName.Y, GateName.Z):
            raise ValueError(f"{name} is not a single-qubit gate without parameters")

        self._graph.add_new_node(name, (qubit, column))
        return self

    def add_rx(self, theta: float, qubit: int, column: int) -> GraphBuilder:
        return self.add_rotation(GateName.RX, theta, qubit, column)

    def add_ry(self, theta: float, qubit: int, column: int) -> GraphBuilder:
        return self.add_rotation(GateName.RY, theta, qubit, column)

    def add_rz(self, theta: float, qubit: int, column: int) -> GraphBuilder:
        return self.add_rotation(GateName.RZ, theta, qubit, column)

    def add_rotation(self, name: GateName, theta: float, qubit: int, column: int) -> GraphBuilder:
        if name not in (GateName.RX, GateName.RY, GateName.RZ):
            raise ValueError(f"{name} is not a rotation gate")

        self._graph.add_new_node(name, (qubit, column), rotation=theta)
        return self

    def add_measure(self, qubit: int, bit: int, column: int) -> GraphBuilder:
        self._graph.add_new_node(GateName.MEASURE, (qubit, column), measure_to=bit)
        return self

    def add_swap(self, qubit1: int, qubit2: int, column: int) -> GraphBuilder:
        first = (qubit1, column)
        second = (qubit2, column)

        self._graph.add_new_node(GateName.SWAP, first)
        self._graph.add_new_node(GateName.SWAP, second)

        self._graph.add_new_edge(_SWAPS_WITH, first, second)
        self._graph.add_new_edge(_SWAPS_WITH, second, first)
        return self

    def add_ch(self, control_qubit: int, target_qubit: int, column: int) -> GraphBuilder:
        return self.add_control(GateName.CH, control_qubit, target_qubit, column)

    def add_cx(self, control_qubit: int, target_qubit: int, column: int) -> GraphBuilder:
        return self.add_control(GateName.CX, control_qubit, target_qubit, column)

    def add_control(self, name: GateName, control_qubit: int, target_qubit: int, column: int) -> GraphBuilder:
        if name not in (GateName.CH, GateName.CX):
            raise ValueError(f"{name} is not an asymmetrical two-qubit controlled gate")

        control = (control_qubit, column)
        target = (target_qubit, column)

        self._graph.add_new_node(name, control)
        self._graph.add_new_node(name, target)

        self._graph.add_new_edge(_TARGETS, control, target)
        self._graph.add_new_edge(_CONTROLLED_BY, target, control)
        return self

    def add_cz(self, qubit1: int, qubit2: int, column: int) -> GraphBuilder:
        first = (qubit1, column)
        second = (qubit2, column)

        self._graph.add_new_node(GateName.CZ, first)
        self._graph.add_new_node(GateName.CZ, second)

        self._graph.add_new_edge(_WORKS_WITH, first, second)
        self._graph.add_new_edge(_WORKS_WITH, second, first)
        return self

    def add_cswap(self, control_qubit: int, target_qubit1: int, target_qubit2: int, column: int) -> GraphBuilder:
        control = (control_qubit, column)
        target1 = (target_qubit1, column)
        target2 = (target_qubit2, column)

        self._graph.add_new_node(GateName.CSWAP, control)
        self._graph.add_new_node(GateName.CSWAP, target1)
        self._graph.add_new_node(GateName.CSWAP, target2)

        self._graph.add_new_edge(_TARGETS, control, target1)
        self._graph.add_new_edge(_TARGETS, control, target2)
        self._graph.add_new_edge(_CONTROLLED_BY, target1, control)
        self._graph.add_new_edge(_SWAPS_WITH, target1, target2)
        self._graph.add_new_edge(_CONTROLLED_BY, target2, control)
        self._graph.add_new_edge(_SWAPS_WITH, target2, target1)
        return self

    def add_ccx(self, control_qubit1: int, control_qubit2: int, target_qubit: int, column: int) -> GraphBuilder:
        control1 = (control_qubit1, column)
        control2 = (control_qubit2, column)
        target = (target_qubit, column)

        self._graph.add_new_node(GateName.CCX, control1)
        self._graph.add_new_node(GateName.CCX, control2)
        self._graph.add_new_node(GateName.CCX, target)

        self._graph.add_new_edge(_TARGETS, control1, target)
        self._graph.add_new_edge(_WORKS_WITH, control1, control2)
        self._graph.add_new_edge(_TARGETS, control2, target)
        self._graph.add_new_edge(_WORKS_WITH, control2, control1)
        self._graph.add_new_edge(_CONTROLLED_BY, target, control1)
        self._graph.add_new_edge(_CONTROLLED_BY, target, control2)
        return self

    def build(self) -> QuantumGraph:
        self._graph.fill_empty_spaces()
        self._graph.fill_positional_edges()
        return self._graph
