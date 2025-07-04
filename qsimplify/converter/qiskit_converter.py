from dataclasses import dataclass
from typing import Callable

import numpy
from qiskit import QuantumCircuit
from qiskit.circuit import CircuitInstruction
from qiskit.circuit.library.standard_gates import YGate
from qiskit.circuit.quantumcircuit import BitLocations

from qsimplify.converter import GatesConverter, GraphConverter
from qsimplify.model import GateName, GraphBuilder, QuantumGate, QuantumGraph

GATES_CONVERTER = GatesConverter()


@dataclass
class ToGraphContext:
    builder: GraphBuilder
    gate_name: GateName
    qubits: list[int]
    bits: list[int]
    params: list

    def unpack(self) -> tuple[GraphBuilder, GateName, list[int], list[int], list]:
        return self.builder, self.gate_name, self.qubits, self.bits, self.params


@dataclass
class FromGraphContext:
    circuit: QuantumCircuit
    gate: QuantumGate

    def unpack(self) -> tuple[QuantumCircuit, QuantumGate]:
        return self.circuit, self.gate


class QiskitConverter(GraphConverter[QuantumCircuit]):
    """Converts a decomposed Qiskit circuit into a quantum graph."""

    def to_graph(self, data: QuantumCircuit, clean_up: bool = True) -> QuantumGraph:
        builder = GraphBuilder()

        for instruction in data.data:
            operation_name = instruction.operation.name

            if operation_name == "barrier":
                continue

            if QiskitConverter._is_instruction_sy(instruction):
                gate_name = GateName.SY
            elif operation_name == "unitary":
                raise ValueError("Non-SY unitary gates are not supported")
            else:
                gate_name = GateName.from_str(operation_name)

            qubits = self._find_qubit_indices(data, instruction)
            bits = self._find_bit_indices(data, instruction)
            params = instruction.operation.params
            context = ToGraphContext(builder, gate_name, qubits, bits, params)
            self._add_to_graph(context)

        return builder.build(clean_up)

    @staticmethod
    def _is_instruction_sy(instruction: CircuitInstruction) -> bool:
        operation = instruction.operation
        square_root = numpy.array(
            [[0.5 + 0.5j, -0.5 - 0.5j], [0.5 + 0.5j, 0.5 + 0.5j]], dtype=complex
        )

        return (
            operation.name == "unitary"
            and operation.num_qubits == 1
            and instruction.operation.num_clbits == 0
            and len(operation.params) == 1
            and numpy.allclose(operation.params[0], square_root)
        )

    @staticmethod
    def _find_qubit_indices(circuit: QuantumCircuit, instruction: CircuitInstruction) -> list[int]:
        qubits = []

        for qubit in instruction.qubits:
            bit_locations: BitLocations = circuit.find_bit(qubit)

            for _, qubit_index in bit_locations.registers:
                qubits.append(qubit_index)

        return qubits

    @staticmethod
    def _find_bit_indices(circuit: QuantumCircuit, instruction: CircuitInstruction) -> list[int]:
        bits = []

        for bit in instruction.clbits:
            bit_locations: BitLocations = circuit.find_bit(bit)

            for _, bit_index in bit_locations.registers:
                bits.append(bit_index)

        return bits

    def _add_to_graph(self, context: ToGraphContext) -> None:
        handler = self._to_graph_handlers.get(context.gate_name)

        if handler:
            handler(context)
        else:
            raise NotImplementedError(f"No to_graph handler for gate type {context.gate_name}")

    @property
    def _to_graph_handlers(self) -> dict[GateName, Callable[[ToGraphContext], None]]:
        return {
            GateName.ID: self._add_id_to_graph,
            GateName.H: self._add_h_to_graph,
            GateName.X: self._add_x_to_graph,
            GateName.Y: self._add_y_to_graph,
            GateName.Z: self._add_z_to_graph,
            GateName.P: self._add_p_to_graph,
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
            GateName.CP: self._add_cp_to_graph,
            GateName.CSWAP: self._add_cswap_to_graph,
            GateName.CCX: self._add_ccx_to_graph,
            GateName.CCZ: self._add_ccz_to_graph,
        }

    @staticmethod
    def _add_id_to_graph(_: ToGraphContext) -> None:
        pass

    @staticmethod
    def _add_h_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_h(qubits[0])

    @staticmethod
    def _add_x_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_x(qubits[0])

    @staticmethod
    def _add_y_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_y(qubits[0])

    @staticmethod
    def _add_z_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_z(qubits[0])

    def _add_p_to_graph(self, context: ToGraphContext) -> None:
        builder, _, qubits, _, params = context.unpack()
        builder.push_p(params[0], qubits[0])

    @staticmethod
    def _add_rx_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, params = context.unpack()
        builder.push_rx(params[0], qubits[0])

    @staticmethod
    def _add_ry_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, params = context.unpack()
        builder.push_ry(params[0], qubits[0])

    @staticmethod
    def _add_rz_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, params = context.unpack()
        builder.push_rz(params[0], qubits[0])

    @staticmethod
    def _add_s_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_s(qubits[0])

    @staticmethod
    def _add_sdg_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_sdg(qubits[0])

    @staticmethod
    def _add_sx_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_sx(qubits[0])

    @staticmethod
    def _add_sy_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_sy(qubits[0])

    @staticmethod
    def _add_t_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_t(qubits[0])

    @staticmethod
    def _add_tdg_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_tdg(qubits[0])

    @staticmethod
    def _add_measure_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, bits, _ = context.unpack()
        builder.push_measure(qubits[0], bits[0])

    @staticmethod
    def _add_swap_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_swap(qubits[0], qubits[1])

    @staticmethod
    def _add_ch_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_ch(qubits[0], qubits[1])

    @staticmethod
    def _add_cx_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_cx(qubits[0], qubits[1])

    @staticmethod
    def _add_cy_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_cy(qubits[0], qubits[1])

    @staticmethod
    def _add_cz_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_cz(qubits[0], qubits[1])

    @staticmethod
    def _add_cp_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, params = context.unpack()
        builder.push_cp(params[0], qubits[0], qubits[1])

    @staticmethod
    def _add_cswap_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_cswap(qubits[0], qubits[1], qubits[2])

    @staticmethod
    def _add_ccx_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_ccx(qubits[0], qubits[1], qubits[2])

    @staticmethod
    def _add_ccz_to_graph(context: ToGraphContext) -> None:
        builder, _, qubits, _, _ = context.unpack()
        builder.push_ccz(qubits[0], qubits[1], qubits[2])

    def from_graph(self, graph: QuantumGraph) -> QuantumCircuit:
        circuit = QuantumCircuit(graph.height, graph.bits)
        gates = GATES_CONVERTER.from_graph(graph)

        for gate in gates:
            context = FromGraphContext(circuit, gate)
            self._add_from_graph(context)

        return circuit

    def _add_from_graph(self, context: FromGraphContext) -> None:
        handler = self._from_graph_handlers.get(context.gate.name)

        if handler:
            handler(context)
        else:
            raise NotImplementedError(f"No from_graph handler for gate type {context.gate.name}")

    @property
    def _from_graph_handlers(self) -> dict[GateName, Callable[[FromGraphContext], None]]:
        return {
            GateName.ID: self._add_id_from_graph,
            GateName.H: self._add_h_from_graph,
            GateName.X: self._add_x_from_graph,
            GateName.Y: self._add_y_from_graph,
            GateName.Z: self._add_z_from_graph,
            GateName.P: self._add_p_from_graph,
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
            GateName.CP: self._add_cp_from_graph,
            GateName.CSWAP: self._add_cswap_from_graph,
            GateName.CCX: self._add_ccx_from_graph,
            GateName.CCZ: self._add_ccz_from_graph,
        }

    @staticmethod
    def _add_id_from_graph(_: FromGraphContext) -> None:
        pass

    @staticmethod
    def _add_h_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.h(gate.qubit)

    @staticmethod
    def _add_x_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.x(gate.qubit)

    @staticmethod
    def _add_y_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.y(gate.qubit)

    @staticmethod
    def _add_z_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.z(gate.qubit)

    @staticmethod
    def _add_p_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.p(gate.angle, gate.qubit)

    @staticmethod
    def _add_rx_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.rx(gate.angle, gate.qubit)

    @staticmethod
    def _add_ry_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.ry(gate.angle, gate.qubit)

    @staticmethod
    def _add_rz_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.rz(gate.angle, gate.qubit)

    @staticmethod
    def _add_s_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.s(gate.qubit)

    @staticmethod
    def _add_sdg_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.sdg(gate.qubit)

    @staticmethod
    def _add_sx_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.sx(gate.qubit)

    @staticmethod
    def _add_sy_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.append(YGate().power(1 / 2), [gate.qubit])

    @staticmethod
    def _add_t_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.t(gate.qubit)

    @staticmethod
    def _add_tdg_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.tdg(gate.qubit)

    @staticmethod
    def _add_measure_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.measure(gate.qubit, gate.bit)

    @staticmethod
    def _add_swap_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.swap(gate.qubit, gate.qubit2)

    @staticmethod
    def _add_ch_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.ch(gate.control_qubit, gate.target_qubit)

    @staticmethod
    def _add_cx_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.cx(gate.control_qubit, gate.target_qubit)

    @staticmethod
    def _add_cy_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.cy(gate.control_qubit, gate.target_qubit)

    @staticmethod
    def _add_cz_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.cz(gate.qubit, gate.qubit2)

    @staticmethod
    def _add_cp_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.cp(gate.angle, gate.control_qubit, gate.target_qubit)

    @staticmethod
    def _add_cswap_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.cswap(gate.control_qubit, gate.target_qubit, gate.target_qubit2)

    @staticmethod
    def _add_ccx_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.ccx(gate.control_qubit, gate.control_qubit2, gate.target_qubit)

    @staticmethod
    def _add_ccz_from_graph(context: FromGraphContext) -> None:
        circuit, gate = context.unpack()
        circuit.ccz(gate.qubit, gate.qubit2, gate.qubit3)
