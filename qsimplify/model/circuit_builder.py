from __future__ import annotations

from qiskit import QuantumCircuit

from qsimplify.model.gate_name import GateName


class CircuitBuilder:
    def __init__(self, qubits: int, name: str = "circuit") -> None:
        self._name = name
        self._circuit = QuantumCircuit(qubits)

    def add_id(self, qubit: int) -> CircuitBuilder:
        return self.add_single(GateName.ID, qubit)

    def add_h(self, qubit: int) -> CircuitBuilder:
        return self.add_single(GateName.H, qubit)

    def add_x(self, qubit: int) -> CircuitBuilder:
        return self.add_single(GateName.X, qubit)

    def add_y(self, qubit: int) -> CircuitBuilder:
        return self.add_single(GateName.Y, qubit)

    def add_z(self, qubit: int) -> CircuitBuilder:
        return self.add_single(GateName.Z, qubit)

    def add_single(self, name: GateName, qubit: int) -> CircuitBuilder:
        if name not in (GateName.ID, GateName.H, GateName.X, GateName.Y, GateName.Z):
            raise ValueError(f"{name} is not a single-qubit gate without parameters")

        match name:
            case GateName.ID:
                self._circuit.id(qubit)
            case GateName.H:
                self._circuit.h(qubit)
            case GateName.X:
                self._circuit.x(qubit)
            case GateName.Y:
                self._circuit.y(qubit)
            case GateName.Z:
                self._circuit.z(qubit)

        return self

    def add_rx(self, theta: float, qubit: int) -> CircuitBuilder:
        return self.add_rotation(GateName.RX, theta, qubit)

    def add_ry(self, theta: float, qubit: int) -> CircuitBuilder:
        return self.add_rotation(GateName.RY, theta, qubit)

    def add_rz(self, theta: float, qubit: int) -> CircuitBuilder:
        return self.add_rotation(GateName.RZ, theta, qubit)

    def add_rotation(self, name: GateName, theta: float, qubit: int) -> CircuitBuilder:
        if name not in (GateName.RX, GateName.RY, GateName.RZ):
            raise ValueError(f"{name} is not a rotation gate")

        match name:
            case GateName.RX:
                self._circuit.rx(theta, qubit)
            case GateName.RY:
                self._circuit.ry(theta, qubit)
            case GateName.RZ:
                self._circuit.rz(theta, qubit)
                return self

        return self

    def add_measure(self, qubit: int, bit: int) -> CircuitBuilder:
        self._circuit.measure(qubit, bit)
        return self

    def add_swap(self, qubit1: int, qubit2: int) -> CircuitBuilder:
        self._circuit.swap(qubit1, qubit2)
        return self

    def add_ch(self, control_qubit: int, target_qubit: int) -> CircuitBuilder:
        return self.add_control(GateName.CH, control_qubit, target_qubit)

    def add_cx(self, control_qubit: int, target_qubit: int) -> CircuitBuilder:
        return self.add_control(GateName.CX, control_qubit, target_qubit)

    def add_control(self, name: GateName, control_qubit: int, target_qubit: int) -> CircuitBuilder:
        if name not in (GateName.CH, GateName.CX):
            raise ValueError(f"{name} is not an asymmetrical two-qubit controlled gate")

        match name:
            case GateName.CH:
                self._circuit.ch(control_qubit, target_qubit)
            case GateName.CX:
                self._circuit.cx(control_qubit, target_qubit)

        return self

    def add_cz(self, qubit1: int, qubit2: int) -> CircuitBuilder:
        self._circuit.cz(qubit1, qubit2)
        return self

    def add_cswap(
        self, control_qubit: int, target_qubit1: int, target_qubit2: int
    ) -> CircuitBuilder:
        self._circuit.cswap(control_qubit, target_qubit1, target_qubit2)
        return self

    def add_ccx(
        self, control_qubit1: int, control_qubit2: int, target_qubit: int
    ) -> CircuitBuilder:
        self._circuit.ccx(control_qubit1, control_qubit2, target_qubit)
        return self

    def build(self) -> QuantumCircuit:
        return self._circuit
