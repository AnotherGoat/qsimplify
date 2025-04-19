from qsimplify.dto import (
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
from qsimplify.dto.quantum_gate import IdGate
from qsimplify.model import QuantumGraph, GraphBuilder
from qsimplify.converter.graph_converter import GraphConverter

from functools import singledispatchmethod


class DtoConverter(GraphConverter[list[QuantumGate]]):
    def to_graph(self, data: list[QuantumGate]) -> QuantumGraph:
        builder = GraphBuilder()

        for gate in data:
            self._add_gate(builder, gate)

        return builder.build()

    @singledispatchmethod
    def _add_gate(self, builder: GraphBuilder, gate: QuantumGate) -> None:
        raise NotImplementedError(f"Unsupported gate: {type(gate)}")

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: IdGate) -> None:
        builder.push_id(gate.qubit)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: HGate) -> None:
        builder.push_h(gate.qubit)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: XGate) -> None:
        builder.push_x(gate.qubit)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: YGate) -> None:
        builder.push_y(gate.qubit)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: ZGate) -> None:
        builder.push_z(gate.qubit)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: RxGate) -> None:
        builder.push_rx(gate.angle, gate.qubit)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: RyGate) -> None:
        builder.push_ry(gate.angle, gate.qubit)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: RzGate) -> None:
        builder.push_rz(gate.angle, gate.qubit)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: MeasureGate) -> None:
        builder.push_measure(gate.qubit, gate.bit)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: SwapGate) -> None:
        builder.push_swap(gate.qubit, gate.qubit2)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: ChGate) -> None:
        builder.push_ch(gate.control_qubit, gate.target_qubit)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: CxGate) -> None:
        builder.push_cx(gate.control_qubit, gate.target_qubit)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: CzGate) -> None:
        builder.push_cz(gate.qubit, gate.qubit2)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: CswapGate) -> None:
        builder.push_cswap(gate.control_qubit, gate.target_qubit, gate.target_qubit2)

    @_add_gate.register
    def _(self, builder: GraphBuilder, gate: CcxGate) -> None:
        builder.push_ccx(gate.control_qubit, gate.control_qubit2, gate.target_qubit)

    def from_graph(self, graph: QuantumGraph) -> list[QuantumGate]:
        pass
