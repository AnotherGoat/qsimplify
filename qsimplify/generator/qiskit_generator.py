"""Contains a code generator for generating Qiskit code from quantum graphs."""

from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction

from qsimplify import math_utils
from qsimplify.converter import GatesConverter
from qsimplify.generator.code_generator import CodeGenerator
from qsimplify.model import GateName, QuantumGate, QuantumGraph

_CIRCUIT_NAME = "circuit"
_GATES_CONVERTER = GatesConverter()
_PI = "numpy.pi"


@dataclass
class _GenerationContext:
    imports: set[str]
    build_steps: list[str]
    gate: QuantumGate


class QiskitGenerator(CodeGenerator):
    """Generates Qiskit code that can build a quantum circuit from a graph."""

    def generate(self, graph: QuantumGraph) -> str:
        """Convert the provided graph into code that uses the Qiskit library."""
        gates = _GATES_CONVERTER.from_graph(graph)
        imports = {"from qiskit import QuantumCircuit"}

        if graph.is_empty():
            build_steps = [f"{_CIRCUIT_NAME} = QuantumCircuit()"]
        elif graph.bits == 0:
            build_steps = [f"{_CIRCUIT_NAME} = QuantumCircuit({graph.height})"]
        else:
            build_steps = [f"{_CIRCUIT_NAME} = QuantumCircuit({graph.height}, {graph.bits})"]

        for gate in gates:
            context = _GenerationContext(imports, build_steps, gate)
            self._generate_gate(context)

        sorted_imports = QiskitGenerator._sort_imports(imports)
        return "\n".join(sorted_imports) + "\n\n" + "\n".join(build_steps)

    @staticmethod
    def _sort_imports(imports: set[str]) -> list[str]:
        return sorted(imports, key=lambda value: " ".join(value.split(" ")[1:]))

    def _generate_gate(self, context: _GenerationContext) -> None:
        handler = self._generate_gate_handlers.get(context.gate.name)

        if handler:
            handler(context)
        else:
            raise NotImplementedError(f"No generate_gate handler for gate type {context.gate.name}")

    @property
    def _generate_gate_handlers(self) -> dict[GateName, Callable[[_GenerationContext], None]]:
        return {
            GateName.ID: self._generate_id,
            GateName.H: self._generate_single_gate,
            GateName.X: self._generate_single_gate,
            GateName.Y: self._generate_single_gate,
            GateName.Z: self._generate_single_gate,
            GateName.P: self._generate_rotation_gate,
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
            GateName.CY: self._generate_control_gate,
            GateName.CZ: self._generate_two_qubit_gate,
            GateName.CP: self._generate_cp,
            GateName.CSWAP: self._generate_cswap,
            GateName.CCX: self._generate_ccx,
            GateName.CCZ: self._generate_ccz,
        }

    @staticmethod
    def _generate_id(_: _GenerationContext) -> None:
        """Adding an identity gate is a no-op."""

    @staticmethod
    def _generate_single_gate(context: _GenerationContext) -> None:
        gate = context.gate
        QiskitGenerator._add_build_step(context, gate.qubit)

    @staticmethod
    def _format_pi_fraction(fraction: Fraction) -> str:
        numerator, denominator = fraction.numerator, fraction.denominator

        if numerator == 0:
            return "0"

        if numerator == denominator:
            return _PI

        if numerator == -denominator:
            return f"-{_PI}"

        if numerator == 1:
            return f"{_PI} / {denominator}"

        if numerator == -1:
            return f"-{_PI} / {denominator}"

        if denominator == 1:
            return f"{numerator} * {_PI}"

        return f"{numerator} * {_PI} / {denominator}"

    @staticmethod
    def _generate_rotation_gate(context: _GenerationContext) -> None:
        imports, gate = context.imports, context.gate
        pi_fraction = math_utils.rationalize_in_terms_of_pi(gate.angle)

        if pi_fraction is None:
            QiskitGenerator._add_build_step(context, gate.angle, gate.qubit)
            return

        if pi_fraction.numerator != 0:
            imports.add("import numpy")

        QiskitGenerator._add_build_step(
            context, QiskitGenerator._format_pi_fraction(pi_fraction), gate.qubit
        )

    @staticmethod
    def _generate_sy_gate(context: _GenerationContext) -> None:
        imports, build_steps, gate = context.imports, context.build_steps, context.gate
        imports.add("from qiskit.circuit.library.standard_gates import YGate")
        build_steps.append(f"{_CIRCUIT_NAME}.append(YGate().power(1 / 2), [{gate.qubit}])")

    @staticmethod
    def _generate_measure(context: _GenerationContext) -> None:
        gate = context.gate
        QiskitGenerator._add_build_step(context, gate.qubit, gate.bit)

    @staticmethod
    def _generate_two_qubit_gate(context: _GenerationContext) -> None:
        gate = context.gate
        QiskitGenerator._add_build_step(context, gate.qubit, gate.qubit2)

    @staticmethod
    def _generate_control_gate(context: _GenerationContext) -> None:
        gate = context.gate
        QiskitGenerator._add_build_step(context, gate.control_qubit, gate.target_qubit)

    @staticmethod
    def _generate_cp(context: _GenerationContext) -> None:
        imports, gate = context.imports, context.gate
        pi_fraction = math_utils.rationalize_in_terms_of_pi(gate.angle)

        if pi_fraction is None:
            QiskitGenerator._add_build_step(
                context, gate.angle, gate.control_qubit, gate.target_qubit
            )
            return

        if pi_fraction.numerator != 0:
            imports.add("import numpy")

        QiskitGenerator._add_build_step(
            context,
            QiskitGenerator._format_pi_fraction(pi_fraction),
            gate.control_qubit,
            gate.target_qubit,
        )

    @staticmethod
    def _generate_cswap(context: _GenerationContext) -> None:
        gate = context.gate
        QiskitGenerator._add_build_step(
            context, gate.control_qubit, gate.target_qubit, gate.target_qubit2
        )

    @staticmethod
    def _generate_ccx(context: _GenerationContext) -> None:
        gate = context.gate
        QiskitGenerator._add_build_step(
            context, gate.control_qubit, gate.control_qubit2, gate.target_qubit
        )

    @staticmethod
    def _generate_ccz(context: _GenerationContext) -> None:
        gate = context.gate
        QiskitGenerator._add_build_step(context, gate.qubit, gate.qubit2, gate.qubit3)

    @staticmethod
    def _add_build_step(context: _GenerationContext, *params: int | float | str) -> None:
        build_steps, gate = context.build_steps, context.gate
        joined_params = ", ".join([str(param) for param in params])
        build_steps.append(f"{_CIRCUIT_NAME}.{gate.name.value}({joined_params})")
