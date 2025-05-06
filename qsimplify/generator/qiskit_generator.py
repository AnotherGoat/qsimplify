from dataclasses import dataclass
from typing import Callable

from qsimplify.converter import GatesConverter
from qsimplify.generator.code_generator import CodeGenerator
from qsimplify.model import GateName, QuantumGate, QuantumGraph

CIRCUIT_NAME = "circuit"
gates_converter = GatesConverter()


@dataclass
class GenerationContext:
    imports: set[str]
    build_steps: list[str]
    gate: QuantumGate

    def unpack(self) -> tuple[set[str], list[str], QuantumGate]:
        return self.imports, self.build_steps, self.gate


class QiskitGenerator(CodeGenerator):
    """Generates Qiskit code that can build a quantum circuit from a graph."""

    def generate(self, graph: QuantumGraph) -> str:
        """Convert the provided graph into coded that uses the Qiskit library."""
        gates = gates_converter.from_graph(graph)
        imports = {"from qiskit import QuantumCircuit"}

        if graph.bits == 0:
            build_steps = [f"{CIRCUIT_NAME} = QuantumCircuit({graph.height})"]
        else:
            build_steps = [f"{CIRCUIT_NAME} = QuantumCircuit({graph.height}, {graph.bits})"]

        for gate in gates:
            context = GenerationContext(imports, build_steps, gate)
            self._generate_gate(context)

        return "\n".join(imports) + "\n\n" + "\n".join(build_steps)

    def _generate_gate(self, context: GenerationContext) -> None:
        handler = self._generate_gate_handlers.get(context.gate.name)

        if handler:
            handler(context)
        else:
            raise NotImplementedError(f"No generate_gate handler for gate type {context.gate.name}")

    @property
    def _generate_gate_handlers(self) -> dict[GateName, Callable[[GenerationContext], None]]:
        return {
            GateName.ID: self._generate_id,
            GateName.H: self._generate_single_gate,
            GateName.X: self._generate_single_gate,
            GateName.Y: self._generate_single_gate,
            GateName.Z: self._generate_single_gate,
            GateName.RX: self._generate_rotation_gate,
            GateName.RY: self._generate_rotation_gate,
            GateName.RZ: self._generate_rotation_gate,
            GateName.S: self._generate_single_gate,
            GateName.SDG: self._generate_single_gate,
            GateName.SX: self._generate_single_gate,
            GateName.SY: self._generate_sy_gate,
            GateName.T: self._generate_single_gate,
            GateName.TDG: self._generate_single_gate,
            GateName.MEASURE: self._generate_measure,
            GateName.SWAP: self._generate_two_qubit_gate,
            GateName.CH: self._generate_control_gate,
            GateName.CX: self._generate_control_gate,
            GateName.CZ: self._generate_two_qubit_gate,
            GateName.CSWAP: self._generate_cswap,
            GateName.CCX: self._generate_ccx,
            GateName.CCZ: self._generate_ccz,
        }

    @staticmethod
    def _generate_id(_: GenerationContext) -> None:
        pass

    @staticmethod
    def _generate_single_gate(context: GenerationContext) -> None:
        _, _, gate = context.unpack()
        QiskitGenerator._add_build_step(context, gate.qubit)

    @staticmethod
    def _generate_rotation_gate(context: GenerationContext) -> None:
        _, _, gate = context.unpack()
        QiskitGenerator._add_build_step(context, gate.angle, gate.qubit)

    @staticmethod
    def _generate_sy_gate(context: GenerationContext) -> None:
        imports, build_steps, gate = context.unpack()
        imports.add("from qiskit.circuit.library.standard_gates import YGate")
        build_steps.append(f"{CIRCUIT_NAME}.append(YGate().power(1 / 2), [{gate.qubit}])")

    @staticmethod
    def _generate_measure(context: GenerationContext) -> None:
        _, _, gate = context.unpack()
        QiskitGenerator._add_build_step(context, gate.qubit, gate.bit)

    @staticmethod
    def _generate_two_qubit_gate(context: GenerationContext) -> None:
        _, _, gate = context.unpack()
        QiskitGenerator._add_build_step(context, gate.qubit, gate.qubit2)

    @staticmethod
    def _generate_control_gate(context: GenerationContext) -> None:
        _, _, gate = context.unpack()
        QiskitGenerator._add_build_step(context, gate.control_qubit, gate.target_qubit)

    @staticmethod
    def _generate_cswap(context: GenerationContext) -> None:
        _, _, gate = context.unpack()
        QiskitGenerator._add_build_step(
            context, gate.control_qubit, gate.target_qubit, gate.target_qubit2
        )

    @staticmethod
    def _generate_ccx(context: GenerationContext) -> None:
        _, _, gate = context.unpack()
        QiskitGenerator._add_build_step(
            context, gate.control_qubit, gate.control_qubit2, gate.target_qubit
        )

    @staticmethod
    def _generate_ccz(context: GenerationContext) -> None:
        _, _, gate = context.unpack()
        QiskitGenerator._add_build_step(context, gate.qubit, gate.qubit2, gate.qubit3)

    @staticmethod
    def _add_build_step(context: GenerationContext, *params: int | float) -> None:
        _, build_steps, gate = context.unpack()

        joined_params = ", ".join([str(param) for param in params])
        build_steps.append(f"{CIRCUIT_NAME}.{gate.name.value}({joined_params})")
