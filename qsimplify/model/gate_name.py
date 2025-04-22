from __future__ import annotations

from enum import Enum


class GateName(str, Enum):
    """The types of quantum gates supported by this library."""

    ID = "id"
    H = "h"
    X = "x"
    Y = "y"
    Z = "z"
    RX = "rx"
    RY = "ry"
    RZ = "rz"
    MEASURE = "measure"
    SWAP = "swap"
    CH = "ch"
    CX = "cx"
    CZ = "cz"
    CSWAP = "cswap"
    CCX = "ccx"

    @classmethod
    def from_str(cls, name: str) -> GateName:
        """
        Obtain a GateName by providing its name as a string.
        Any combination of uppercase and lowercase letters is accepted.
        """
        try:
            return cls(name.lower())
        except ValueError as error:
            raise ValueError(f"'{name}' is not a valid GateName") from error

    def number_of_qubits(self) -> int:
        """
        Get the number of qubits used by this type of gate.
        Identity gates return 0 because they add no value to the circuit.
        """
        match self:
            case GateName.ID:
                return 0
            case GateName.SWAP | GateName.CH | GateName.CX | GateName.CZ:
                return 2
            case GateName.CSWAP | GateName.CCX:
                return 3
            case _:
                return 1

    def is_controlled(self) -> bool:
        """Check whether this gate type has control and target qubits or not."""
        return self.control_qubit_count() > 0

    def control_qubit_count(self) -> int:
        """Get the number of control qubits used by this type of gate."""
        match self:
            case GateName.CH | GateName.CX | GateName.CZ | GateName.CSWAP:
                return 1
            case GateName.CCX:
                return 2
            case _:
                return 0

    def is_single_controlled(self) -> bool:
        """Check whether this gate type has a single control and a single target qubit."""
        return self.control_qubit_count() == 1 and self.target_qubit_count() == 1

    def target_qubit_count(self) -> int:
        """
        Get the number of qubits affected by this type of gate.
        Identity gates return 0 because they target a single qubit, but make no changes to it.
        """
        match self:
            case GateName.ID | GateName.MEASURE:
                return 0
            case GateName.SWAP | GateName.CSWAP:
                return 2
            case _:
                return 1
