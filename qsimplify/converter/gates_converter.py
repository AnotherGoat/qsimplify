from dataclasses import dataclass
from typing import Callable, Never, assert_never

from qsimplify.converter.graph_converter import GraphConverter
from qsimplify.model import (
    CcxGate,
    ChGate,
    CswapGate,
    CxGate,
    CzGate,
    GateName,
    GraphBuilder,
    GraphNode,
    HGate,
    MeasureGate,
    Position,
    QuantumGate,
    QuantumGraph,
    RxGate,
    RyGate,
    RzGate,
    SwapGate,
    XGate,
    YGate,
    ZGate,
)
from qsimplify.model.quantum_gate import (
    CczGate,
    CyGate,
    SdgGate,
    SGate,
    SxGate,
    SyGate,
    TdgGate,
    TGate,
)


@dataclass
class ToGraphContext:
    builder: GraphBuilder
    gate: QuantumGate

    def unpack(self) -> tuple[GraphBuilder, QuantumGate]:
        return self.builder, self.gate


@dataclass
class FromGraphContext:
    graph: QuantumGraph
    node: GraphNode
    gates: list[QuantumGate]
    skipped: set[Position]

    def unpack(self) -> tuple[QuantumGraph, GraphNode, list[QuantumGate], set[Position]]:
        return self.graph, self.node, self.gates, self.skipped


class GatesConverter(GraphConverter[list[QuantumGate]]):
    def to_graph(self, data: list[QuantumGate], clean_up: bool = True) -> QuantumGraph:
        builder = GraphBuilder()

        for gate in data:
            context = ToGraphContext(builder, gate)
            self._add_to_graph(context)

        return builder.build(clean_up)

    @property
    def _to_graph_handlers(self) -> dict[GateName, Callable[[ToGraphContext], None]]:
        return {
            GateName.ID: self._add_id_to_graph,
            GateName.H: self._add_h_to_graph,
            GateName.X: self._add_x_to_graph,
            GateName.Y: self._add_y_to_graph,
            GateName.Z: self._add_z_to_graph,
            GateName.RX: self._add_rx_to_graph,
            GateName.RY: self._add_ry_to_graph,
            GateName.RZ: self._add_rz_to_graph,
            GateName.S: self._add_s_to_graph,
            GateName.SDG: self._add_sdg_to_graph,
            GateName.SX: self._add_sx_to_graph,
            GateName.SY: self._add_sy_to_graph,
            GateName.T: self._add_t_to_graph,
            GateName.TDG: self._add_tdg_to_graph,
            GateName.MEASURE: self._add_measure_to_graph,
            GateName.SWAP: self._add_swap_to_graph,
            GateName.CH: self._add_ch_to_graph,
            GateName.CX: self._add_cx_to_graph,
            GateName.CY: self._add_cy_to_graph,
            GateName.CZ: self._add_cz_to_graph,
            GateName.CSWAP: self._add_cswap_to_graph,
            GateName.CCX: self._add_ccx_to_graph,
            GateName.CCZ: self._add_ccz_to_graph,
        }

    def _add_to_graph(self, context: ToGraphContext) -> None:
        handler = self._to_graph_handlers.get(context.gate.name)

        if handler:
            handler(context)
        else:
            raise NotImplementedError(f"No to_graph handler for gate type {context.gate.name}")

    @staticmethod
    def _add_id_to_graph(_: ToGraphContext) -> None:
        """Adding an identity gate is a no-op."""

    @staticmethod
    def _add_h_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_h(gate.qubit)

    @staticmethod
    def _add_x_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_x(gate.qubit)

    @staticmethod
    def _add_y_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_y(gate.qubit)

    @staticmethod
    def _add_z_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_z(gate.qubit)

    @staticmethod
    def _add_rx_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_rx(gate.angle, gate.qubit)

    @staticmethod
    def _add_ry_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_ry(gate.angle, gate.qubit)

    @staticmethod
    def _add_rz_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_rz(gate.angle, gate.qubit)

    @staticmethod
    def _add_s_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_s(gate.qubit)

    @staticmethod
    def _add_sdg_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_sdg(gate.qubit)

    @staticmethod
    def _add_sx_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_sx(gate.qubit)

    @staticmethod
    def _add_sy_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_sy(gate.qubit)

    @staticmethod
    def _add_t_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_t(gate.qubit)

    @staticmethod
    def _add_tdg_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_tdg(gate.qubit)

    @staticmethod
    def _add_measure_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_measure(gate.qubit, gate.bit)

    @staticmethod
    def _add_swap_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_swap(gate.qubit, gate.qubit2)

    @staticmethod
    def _add_ch_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_ch(gate.control_qubit, gate.target_qubit)

    @staticmethod
    def _add_cx_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_cx(gate.control_qubit, gate.target_qubit)

    @staticmethod
    def _add_cy_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_cy(gate.control_qubit, gate.target_qubit)

    @staticmethod
    def _add_cz_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_cz(gate.qubit, gate.qubit2)

    @staticmethod
    def _add_cswap_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_cswap(gate.control_qubit, gate.target_qubit, gate.target_qubit2)

    @staticmethod
    def _add_ccx_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_ccx(gate.control_qubit, gate.control_qubit2, gate.target_qubit)

    @staticmethod
    def _add_ccz_to_graph(context: ToGraphContext) -> None:
        builder, gate = context.unpack()
        builder.push_ccz(gate.qubit, gate.qubit2, gate.qubit3)

    def from_graph(self, graph: QuantumGraph) -> list[QuantumGate]:
        gates = []
        skipped = set()

        for column in range(graph.width):
            for row in range(graph.height):
                position = Position(row, column)

                if position in skipped:
                    continue

                context = FromGraphContext(graph, graph[position], gates, skipped)
                self._add_from_graph(context)

        return gates

    def _add_from_graph(self, context: FromGraphContext) -> None:
        handler = self._from_graph_handlers.get(context.node.name)

        if handler:
            handler(context)
        else:
            raise NotImplementedError(f"No from_graph handler for gate type {context.node.name}")

    @property
    def _from_graph_handlers(self) -> dict[GateName, Callable[[FromGraphContext], None]]:
        return {
            GateName.ID: self._add_id_from_graph,
            GateName.H: self._add_h_from_graph,
            GateName.X: self._add_x_from_graph,
            GateName.Y: self._add_y_from_graph,
            GateName.Z: self._add_z_from_graph,
            GateName.RX: self._add_rx_from_graph,
            GateName.RY: self._add_ry_from_graph,
            GateName.RZ: self._add_rz_from_graph,
            GateName.S: self._add_s_from_graph,
            GateName.SDG: self._add_sdg_from_graph,
            GateName.SX: self._add_sx_from_graph,
            GateName.SY: self._add_sy_from_graph,
            GateName.T: self._add_t_from_graph,
            GateName.TDG: self._add_tdg_from_graph,
            GateName.MEASURE: self._add_measure_from_graph,
            GateName.SWAP: self._add_swap_from_graph,
            GateName.CH: self._add_ch_from_graph,
            GateName.CX: self._add_cx_from_graph,
            GateName.CY: self._add_cy_from_graph,
            GateName.CZ: self._add_cz_from_graph,
            GateName.CSWAP: self._add_cswap_from_graph,
            GateName.CCX: self._add_ccx_from_graph,
            GateName.CCZ: self._add_ccz_from_graph,
        }

    @staticmethod
    def _add_id_from_graph(_: FromGraphContext) -> None:
        pass

    @staticmethod
    def _add_single_gate_from_graph(
        context: FromGraphContext, factory: Callable[..., QuantumGate]
    ) -> None:
        _, node, gates, _ = context.unpack()

        gate = factory(qubit=node.position.row)
        gates.append(gate)

    @staticmethod
    def _add_h_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_single_gate_from_graph(context, HGate)

    @staticmethod
    def _add_x_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_single_gate_from_graph(context, XGate)

    @staticmethod
    def _add_y_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_single_gate_from_graph(context, YGate)

    @staticmethod
    def _add_z_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_single_gate_from_graph(context, ZGate)

    @staticmethod
    def _add_rotation_gate_from_graph(
        context: FromGraphContext, factory: Callable[..., QuantumGate]
    ) -> None:
        _, node, gates, _ = context.unpack()

        gate = factory(qubit=node.position.row, angle=node.angle)
        gates.append(gate)

    @staticmethod
    def _add_rx_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_rotation_gate_from_graph(context, RxGate)

    @staticmethod
    def _add_ry_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_rotation_gate_from_graph(context, RyGate)

    @staticmethod
    def _add_rz_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_rotation_gate_from_graph(context, RzGate)

    @staticmethod
    def _add_s_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_single_gate_from_graph(context, SGate)

    @staticmethod
    def _add_sdg_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_single_gate_from_graph(context, SdgGate)

    @staticmethod
    def _add_sx_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_single_gate_from_graph(context, SxGate)

    @staticmethod
    def _add_sy_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_single_gate_from_graph(context, SyGate)

    @staticmethod
    def _add_t_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_single_gate_from_graph(context, TGate)

    @staticmethod
    def _add_tdg_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_single_gate_from_graph(context, TdgGate)

    @staticmethod
    def _add_measure_from_graph(context: FromGraphContext) -> None:
        _, node, gates, _ = context.unpack()

        gate = MeasureGate(qubit=node.position.row, bit=node.bit)
        gates.append(gate)

    @staticmethod
    def _add_swap_from_graph(context: FromGraphContext) -> None:
        graph, node, gates, skipped = context.unpack()
        edges = graph.node_edge_data(node.position)

        if edges is None:
            assert_never(edges)

        other_position = edges.swaps_with.position

        gate = SwapGate(qubit=node.position.row, qubit2=other_position.row)
        gates.append(gate)
        skipped.add(other_position)

    @staticmethod
    def _add_control_gate_from_graph(
        context: FromGraphContext, factory: Callable[..., QuantumGate]
    ) -> None:
        graph, node, gates, skipped = context.unpack()
        edges = graph.node_edge_data(node.position)

        if edges is None:
            assert_never(edges)

        is_target = edges.targets == []

        if is_target:
            control_position = edges.controlled_by[0].position
            target_position = node.position
        else:
            control_position = node.position
            target_position = edges.targets[0].position

        gate = factory(control_qubit=control_position.row, target_qubit=target_position.row)
        gates.append(gate)
        skipped.add(control_position)
        skipped.add(target_position)

    @staticmethod
    def _add_ch_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_control_gate_from_graph(context, ChGate)

    @staticmethod
    def _add_cx_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_control_gate_from_graph(context, CxGate)

    @staticmethod
    def _add_cy_from_graph(context: FromGraphContext) -> None:
        GatesConverter._add_control_gate_from_graph(context, CyGate)

    @staticmethod
    def _add_cz_from_graph(context: FromGraphContext) -> None:
        graph, node, gates, skipped = context.unpack()
        edges = graph.node_edge_data(node.position)

        if edges is None:
            assert_never(edges)

        other_position = edges.works_with[0].position

        gate = CzGate(qubit=node.position.row, qubit2=other_position.row)
        gates.append(gate)
        skipped.add(other_position)

    @staticmethod
    def _add_cswap_from_graph(context: FromGraphContext) -> None:
        graph, node, gates, skipped = context.unpack()
        edges = graph.node_edge_data(node.position)

        if edges is None:
            assert_never(edges)

        is_target = edges.targets == []

        if is_target:
            control_position = edges.controlled_by[0].position
            target_position = node.position
            target2_position = edges.swaps_with.position
        else:
            control_position = node.position
            target_position = edges.targets[0].position
            target2_position = edges.targets[1].position

        gate = CswapGate(
            control_qubit=control_position.row,
            target_qubit=target_position.row,
            target_qubit2=target2_position.row,
        )
        gates.append(gate)
        skipped.add(control_position)
        skipped.add(target_position)
        skipped.add(target2_position)

    @staticmethod
    def _add_ccx_from_graph(context: FromGraphContext) -> None:
        graph, node, gates, skipped = context.unpack()
        edges = graph.node_edge_data(node.position)

        if edges is None:
            assert_never(edges)

        is_target = edges.targets == []

        if is_target:
            control_position = edges.controlled_by[0].position
            control2_position = edges.controlled_by[1].position
            target_position = node.position
        else:
            control_position = node.position
            control2_position = edges.works_with[0].position
            target_position = edges.targets[0].position

        gate = CcxGate(
            control_qubit=control_position.row,
            control_qubit2=control2_position.row,
            target_qubit=target_position.row,
        )
        gates.append(gate)
        skipped.add(control_position)
        skipped.add(control2_position)
        skipped.add(target_position)

    @staticmethod
    def _add_ccz_from_graph(context: FromGraphContext) -> None:
        graph, node, gates, skipped = context.unpack()
        edges = graph.node_edge_data(node.position)

        if edges is None:
            assert_never(edges)

        other_position = edges.works_with[0].position
        other_position2 = edges.works_with[1].position

        gate = CczGate(
            qubit=node.position.row, qubit2=other_position.row, qubit3=other_position2.row
        )
        gates.append(gate)
        skipped.add(other_position)
        skipped.add(other_position2)
