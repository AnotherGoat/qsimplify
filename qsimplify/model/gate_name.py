from __future__ import annotations

from enum import Enum


class GateName(str, Enum):
    """The types of quantum gates supported by this library."""

    ID = "id"
    """The identity gate. It has no practical effect."""
    H = "h"
    """Single-qubit Hadamard gate."""
    X = "x"
    """Single-qubit X gate. Also known as the NOT gate."""
    Y = "y"
    """Single-qubit Y gate."""
    Z = "z"
    """Single-qubit Z gate."""
    RX = "rx"
    """Single-qubit rotation gate, which rotates around the X axis."""
    RY = "ry"
    """Single-qubit rotation gate, which rotates around the Y axis."""
    RZ = "rz"
    """Single-qubit rotation gate, which rotates around the Z axis."""
    S = "s"
    """Single-qubit S gate. Also known as the sqrt(Z) gate."""
    SDG = "sdg"
    """Single-qubit S dagger gate. The conjugate transpose of the S gate."""
    SX = "sx"
    """Single-qubit sqrt(X) gate."""
    SY = "sy"
    """Single-qubit sqrt(Y) gate."""
    T = "t"
    """Single-qubit T gate. Equivalent to Z^0.25."""
    TDG = "tdg"
    """Single-qubit T dagger gate. The conjugate transpose of the T gate."""
    MEASURE = "measure"
    """Single-qubit measurement gate. Stores its results on a particular bit."""
    SWAP = "swap"
    """Two-qubit SWAP gate."""
    CH = "ch"
    """Two-qubit controlled Hadamard gate."""
    CX = "cx"
    """Two-qubit controlled X gate. Also known as the CNOT gate."""
    CY = "cy"
    """Two-qubit controlled Y gate."""
    CZ = "cz"
    """Two-qubit controlled Z gate."""
    CSWAP = "cswap"
    """Three-qubit controlled SWAP gate."""
    CCX = "ccx"
    """Three-qubit X Gate, controlled by 2 qubits. Also known as the Toffoli gate."""
    CCZ = "ccz"
    """Three-qubit Z Gate, controlled by 2 qubits."""

    @classmethod
    def from_str(cls, name: str) -> GateName:
        """Obtain a GateName by providing its name as a string.

        Any combination of uppercase and lowercase letters is accepted.
        """
        try:
            return cls(name.lower())
        except ValueError as error:
            raise ValueError(f"'{name}' is not a valid GateName") from error

    def is_rotation(self) -> bool:
        """Check whether this gate type is a rotation or not."""
        return self in {GateName.RX, GateName.RY, GateName.RZ}

    def is_square_root(self) -> bool:
        """Check whether this gate type is a square root or not."""
        return self in {GateName.S, GateName.SDG, GateName.SX, GateName.SY}

    def number_of_qubits(self) -> int:
        """Get the number of qubits used by this type of gate.

        Identity gates return 0 because they add no value to the circuit.
        """
        match self:
            case GateName.ID:
                return 0
            case GateName.SWAP | GateName.CH | GateName.CX | GateName.CY | GateName.CZ:
                return 2
            case GateName.CSWAP | GateName.CCX | GateName.CCZ:
                return 3
            case _:
                return 1

    def is_controlled(self) -> bool:
        """Check whether this gate type has control and target qubits or not."""
        return self.control_qubit_count() > 0

    def control_qubit_count(self) -> int:
        """Get the number of control qubits used by this type of gate."""
        match self:
            case GateName.CH | GateName.CX | GateName.CY | GateName.CZ | GateName.CSWAP:
                return 1
            case GateName.CCX | GateName.CCZ:
                return 2
            case _:
                return 0

    def target_qubit_count(self) -> int:
        """Get the number of qubits affected by this type of gate.

        Identity gates return 0 because they target a single qubit, but make no changes to it.
        """
        match self:
            case GateName.ID | GateName.MEASURE:
                return 0
            case GateName.SWAP | GateName.CSWAP:
                return 2
            case _:
                return 1

    def is_single_controlled(self) -> bool:
        """Check whether this gate type has a single control and a single target qubit."""
        return self.control_qubit_count() == 1 and self.target_qubit_count() == 1
