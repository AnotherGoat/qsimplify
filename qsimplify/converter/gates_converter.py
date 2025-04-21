from dataclasses import dataclass
from typing import Callable

from qsimplify.converter.graph_converter import GraphConverter
from qsimplify.model import (
    QuantumGate,
    HGate,
    XGate,
    YGate,
    ZGate,
    RxGate,
    RyGate,
    RzGate,
    MeasureGate,
    SwapGate,
    ChGate,
    CxGate,
    CzGate,
    CswapGate,
    CcxGate,
)
from qsimplify.model.quantum_gate import IdGate
from qsimplify.model import QuantumGraph, GraphBuilder, Position, GraphNode, GateName


@dataclass
class FromGraphContext:
    graph: QuantumGraph
    node: GraphNode
    gates: list[QuantumGate]
    skipped: set[Position]

    def unpack(self) -> tuple[QuantumGraph, GraphNode, list[QuantumGate], set[Position]]:
        return self.graph, self.node, self.gates, self.skipped


class GatesConverter(GraphConverter[list[QuantumGate]]):
    def to_graph(self, data: list[QuantumGate]) -> QuantumGraph:
        builder = GraphBuilder()

        for gate in data:
            self._add_to_graph(builder, gate)

        return builder.build()

    @property
    def _to_graph_handlers(self) -> dict[GateName, Callable[[GraphBuilder, QuantumGate], None]]:
        return {
            GateName.ID: self._add_id_to_graph,
            GateName.H: self._add_h_to_graph,
            GateName.X: self._add_x_to_graph,
            GateName.Y: self._add_y_to_graph,
            GateName.Z: self._add_z_to_graph,
            GateName.RX: self._add_rx_to_graph,
            GateName.RY: self._add_ry_to_graph,
            GateName.RZ: self._add_rz_to_graph,
            GateName.MEASURE: self._add_measure_to_graph,
            GateName.SWAP: self._add_swap_to_graph,
            GateName.CH: self._add_ch_to_graph,
            GateName.CX: self._add_cx_to_graph,
            GateName.CZ: self._add_cz_to_graph,
            GateName.CSWAP: self._add_cswap_to_graph,
            GateName.CCX: self._add_ccx_to_graph,
        }

    def _add_to_graph(self, builder: GraphBuilder, gate: QuantumGate) -> None:
        handler = self._to_graph_handlers.get(gate.name)

        if handler:
            handler(builder, gate)
        else:
            raise NotImplementedError(f"No to_graph handler for gate type {gate.name}")

    @staticmethod
    def _add_id_to_graph(builder: GraphBuilder, gate: IdGate) -> None:
        pass

    @staticmethod
    def _add_h_to_graph(builder: GraphBuilder, gate: HGate) -> None:
        builder.push_h(gate.qubit)

    @staticmethod
    def _add_x_to_graph(builder: GraphBuilder, gate: XGate) -> None:
        builder.push_x(gate.qubit)

    @staticmethod
    def _add_y_to_graph(builder: GraphBuilder, gate: YGate) -> None:
        builder.push_y(gate.qubit)

    @staticmethod
    def _add_z_to_graph(builder: GraphBuilder, gate: ZGate) -> None:
        builder.push_z(gate.qubit)

    @staticmethod
    def _add_rx_to_graph(builder: GraphBuilder, gate: RxGate) -> None:
        builder.push_rx(gate.angle, gate.qubit)

    @staticmethod
    def _add_ry_to_graph(builder: GraphBuilder, gate: RyGate) -> None:
        builder.push_ry(gate.angle, gate.qubit)

    @staticmethod
    def _add_rz_to_graph(builder: GraphBuilder, gate: RzGate) -> None:
        builder.push_rz(gate.angle, gate.qubit)

    @staticmethod
    def _add_measure_to_graph(builder: GraphBuilder, gate: MeasureGate) -> None:
        builder.push_measure(gate.qubit, gate.bit)

    @staticmethod
    def _add_swap_to_graph(builder: GraphBuilder, gate: SwapGate) -> None:
        builder.push_swap(gate.qubit, gate.qubit2)

    @staticmethod
    def _add_ch_to_graph(builder: GraphBuilder, gate: ChGate) -> None:
        builder.push_ch(gate.control_qubit, gate.target_qubit)

    @staticmethod
    def _add_cx_to_graph(builder: GraphBuilder, gate: CxGate) -> None:
        builder.push_cx(gate.control_qubit, gate.target_qubit)

    @staticmethod
    def _add_cz_to_graph(builder: GraphBuilder, gate: CzGate) -> None:
        builder.push_cz(gate.qubit, gate.qubit2)

    @staticmethod
    def _add_cswap_to_graph(builder: GraphBuilder, gate: CswapGate) -> None:
        builder.push_cswap(gate.control_qubit, gate.target_qubit, gate.target_qubit2)

    @staticmethod
    def _add_ccx_to_graph(builder: GraphBuilder, gate: CcxGate) -> None:
        builder.push_ccx(gate.control_qubit, gate.control_qubit2, gate.target_qubit)

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
            GateName.MEASURE: self._add_measure_from_graph,
            GateName.SWAP: self._add_swap_from_graph,
            GateName.CH: self._add_ch_from_graph,
            GateName.CX: self._add_cx_from_graph,
            GateName.CZ: self._add_cz_from_graph,
            GateName.CSWAP: self._add_cswap_from_graph,
            GateName.CCX: self._add_ccx_from_graph,
        }

    @staticmethod
    def _add_id_from_graph(context: FromGraphContext) -> None:
        pass

    @staticmethod
    def _add_single_gate_from_graph(
        context: FromGraphContext, factory: Callable[..., QuantumGate]
    ) -> None:
        graph, node, gates, skipped = context.unpack()

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
        graph, node, gates, skipped = context.unpack()

        gate = factory(qubit=node.position.row, angle=node.rotation)
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
    def _add_measure_from_graph(context: FromGraphContext) -> None:
        graph, node, gates, skipped = context.unpack()

        gate = MeasureGate(qubit=node.position.row, bit=node.measure_to)
        gates.append(gate)

    @staticmethod
    def _add_swap_from_graph(context: FromGraphContext) -> None:
        graph, node, gates, skipped = context.unpack()
        edges = graph.node_edge_data(node.position)
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
    def _add_cz_from_graph(context: FromGraphContext) -> None:
        graph, node, gates, skipped = context.unpack()
        edges = graph.node_edge_data(node.position)
        other_position = edges.works_with[0].position

        gate = CzGate(qubit=node.position.row, qubit2=other_position.row)
        gates.append(gate)
        skipped.add(other_position)

    @staticmethod
    def _add_cswap_from_graph(context: FromGraphContext) -> None:
        graph, node, gates, skipped = context.unpack()
        edges = graph.node_edge_data(node.position)
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
