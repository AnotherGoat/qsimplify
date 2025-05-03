from __future__ import annotations

import math
from typing import Annotated, Literal, Self, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_core import ErrorDetails

from qsimplify.model import GateName


def _check_index(value: int) -> int:
    if value < 0:
        raise ValueError("it must be 0 or positive")

    return value


def _check_angle(value: float) -> float:
    if value < 0 or value >= 2 * math.tau:
        raise ValueError(f"it must be between 0 and {2 * math.tau} radians")

    return value


def _check_indices(fields: list[str], values: list[int]) -> None:
    if len(set(values)) != len(values):
        raise ValueError(f"{_format_fields(fields)} must be different")


def _format_fields(fields: list[str]) -> str:
    if len(fields) == 0:
        return ""

    if len(fields) == 1:
        return fields[0]

    if len(fields) == 2:
        return f"{fields[0]} and {fields[1]}"

    return ", ".join(fields[:-1]) + f" and {fields[-1]}"


class BaseGate(BaseModel):
    name: GateName
    model_config = ConfigDict(extra="forbid")


class SingleGate(BaseGate):
    qubit: int

    @field_validator("qubit")
    @classmethod
    def _validate_qubit(cls, value: int) -> int:
        return _check_index(value)


class IdGate(SingleGate):
    """The identity gate. It has no practical effect."""

    name: Literal[GateName.ID] = GateName.ID


class HGate(SingleGate):
    """Single-qubit Hadamard gate."""

    name: Literal[GateName.H] = GateName.H


class XGate(SingleGate):
    """Single-qubit X gate. Also known as the NOT gate."""

    name: Literal[GateName.X] = GateName.X


class YGate(SingleGate):
    """Single-qubit Y gate."""

    name: Literal[GateName.Y] = GateName.Y


class ZGate(SingleGate):
    """Single-qubit Z gate."""

    name: Literal[GateName.Z] = GateName.Z


class RotationGate(SingleGate):
    angle: float

    @field_validator("angle")
    @classmethod
    def _validate_angle(cls, value: float) -> float:
        return _check_angle(value)


class RxGate(RotationGate):
    """Single-qubit rotation gate, which rotates around the X axis."""

    name: Literal[GateName.RX] = GateName.RX


class RyGate(RotationGate):
    """Single-qubit rotation gate, which rotates around the Y axis."""

    name: Literal[GateName.RY] = GateName.RY


class RzGate(RotationGate):
    """Single-qubit rotation gate, which rotates around the Z axis."""

    name: Literal[GateName.RZ] = GateName.RZ


class SGate(SingleGate):
    """Single-qubit S gate. Also known as the sqrt(Z) gate."""

    name: Literal[GateName.S] = GateName.S


class SdgGate(SingleGate):
    """Single-qubit S dagger gate. The conjugate transpose of the S gate."""

    name: Literal[GateName.SDG] = GateName.SDG


class SxGate(SingleGate):
    """Single-qubit sqrt(X) gate."""

    name: Literal[GateName.SX] = GateName.SX


class SyGate(SingleGate):
    """Single-qubit sqrt(Y) gate."""

    name: Literal[GateName.SY] = GateName.SY


class TGate(SingleGate):
    """Single-qubit T gate. Equivalent to Z^0.25."""

    name: Literal[GateName.T] = GateName.T


class TdgGate(SingleGate):
    """Single-qubit T dagger gate. The conjugate transpose of the T gate."""

    name: Literal[GateName.TDG] = GateName.TDG


class MeasureGate(SingleGate):
    """Single-qubit measurement gate. Stores its results on a particular bit."""

    name: Literal[GateName.MEASURE] = GateName.MEASURE
    bit: int

    @field_validator("bit")
    @classmethod
    def _validate_bit(cls, value: int) -> int:
        return _check_index(value)


class TwoQubitGate(BaseGate):
    qubit: int
    qubit2: int

    @field_validator("qubit")
    @classmethod
    def _validate_qubit(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("qubit2")
    @classmethod
    def _validate_qubit2(cls, value: int) -> int:
        return _check_index(value)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        _check_indices(["qubit", "qubit2"], [self.qubit, self.qubit2])
        return self


class SwapGate(TwoQubitGate):
    """Two-qubit SWAP gate."""

    name: Literal[GateName.SWAP] = GateName.SWAP


class SingleControlledGate(BaseGate):
    control_qubit: int
    target_qubit: int

    @field_validator("control_qubit")
    @classmethod
    def _validate_control_qubit(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("target_qubit")
    @classmethod
    def _validate_target_qubit(cls, value: int) -> int:
        return _check_index(value)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        _check_indices(["control_qubit", "target_qubit"], [self.control_qubit, self.target_qubit])
        return self


class ChGate(SingleControlledGate):
    """Two-qubit controlled Hadamard gate."""

    name: Literal[GateName.CH] = GateName.CH


class CxGate(SingleControlledGate):
    """Two-qubit controlled X gate. Also known as the CNOT gate."""

    name: Literal[GateName.CX] = GateName.CX


class CzGate(TwoQubitGate):
    """Two-qubit controlled Z gate."""

    name: Literal[GateName.CZ] = GateName.CZ


class CswapGate(BaseGate):
    """Three-qubit controlled SWAP gate."""

    name: Literal[GateName.CSWAP] = GateName.CSWAP
    control_qubit: int
    target_qubit: int
    target_qubit2: int

    @field_validator("control_qubit")
    @classmethod
    def _validate_control_qubit(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("target_qubit")
    @classmethod
    def _validate_target_qubit(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("target_qubit2")
    @classmethod
    def _validate_target_qubit2(cls, value: int) -> int:
        return _check_index(value)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        _check_indices(
            ["control_qubit", "target_qubit", "target_qubit2"],
            [self.control_qubit, self.target_qubit, self.target_qubit2],
        )
        return self


class CcxGate(BaseGate):
    """Three-qubit X Gate, controlled by 2 qubits. Also known as the CCNOT or Toffoli gate."""

    name: Literal[GateName.CCX] = GateName.CCX
    control_qubit: int
    control_qubit2: int
    target_qubit: int

    @field_validator("control_qubit")
    @classmethod
    def _validate_control_qubit(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("control_qubit2")
    @classmethod
    def _validate_control_qubit2(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("target_qubit")
    @classmethod
    def _validate_target_qubit(cls, value: int) -> int:
        return _check_index(value)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        _check_indices(
            ["control_qubit", "control_qubit2", "target_qubit"],
            [self.control_qubit, self.control_qubit2, self.target_qubit],
        )
        return self


class CczGate(BaseGate):
    """Three-qubit Z Gate, controlled by 2 qubits."""

    name: Literal[GateName.CCZ] = GateName.CCZ
    qubit: int
    qubit2: int
    qubit3: int

    @field_validator("qubit")
    @classmethod
    def _validate_qubit(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("qubit2")
    @classmethod
    def _validate_qubit2(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("qubit3")
    @classmethod
    def _validate_qubit3(cls, value: int) -> int:
        return _check_index(value)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        _check_indices(["qubit", "qubit2", "qubit3"], [self.qubit, self.qubit2, self.qubit3])
        return self


QuantumGate = Annotated[
    Union[
        IdGate,
        HGate,
        XGate,
        YGate,
        ZGate,
        RxGate,
        RyGate,
        RzGate,
        SGate,
        SdgGate,
        SxGate,
        SyGate,
        TGate,
        TdgGate,
        MeasureGate,
        SwapGate,
        ChGate,
        CxGate,
        CzGate,
        CswapGate,
        CcxGate,
        CczGate,
    ],
    Field(discriminator="name"),
]
"""Any of the gates that may compose a quantum circuit."""

_gate_adapter = TypeAdapter(QuantumGate)


type Errors = dict[int, list[str]]


class GatesValidationError(Exception):
    errors: Errors

    def __init__(self, errors: Errors) -> None:
        self.errors = errors
        super().__init__(f"Gates validation failed {self.errors}")


def parse_gates(gates: list[dict]) -> list[QuantumGate]:
    """Validates and converts a JSON list of dictionaries into a list of quantum gates."""
    output: list[QuantumGate] = []
    errors: Errors = {}

    for index, json in enumerate(gates):
        try:
            output.append(_gate_adapter.validate_python(json))
        except ValidationError as error:
            errors[index] = _extract_error_messages(error)
        except Exception as error:
            errors[index] = [f"unknown: {error}"]

    if len(errors) != 0:
        raise GatesValidationError(errors)

    return output


def _extract_error_messages(validation_error: ValidationError) -> list[str]:
    return [_format_error_message(error) for error in validation_error.errors()]


def _format_error_message(error: ErrorDetails) -> str:
    location = error["loc"][-1]
    message = error["msg"]
    return f"{location}: {message}"
