from __future__ import annotations

import math
from typing import Annotated, Any, Literal, Self, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

from qsimplify.model import GateName


def _check_index(value: int) -> int:
    if value < 0:
        raise ValueError("it must be 0 or positive")

    return value


def _check_angle(value: float) -> float:
    if value < 0 or value >= math.tau:
        raise ValueError(f"it must be between 0 and {math.tau} radians")

    return value


def _check_indexes(fields: list[str], values: list[int]) -> None:
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
    def validate_qubit(cls, value: int) -> int:
        return _check_index(value)


class IdGate(SingleGate):
    name: Literal[GateName.ID] = GateName.ID


class HGate(SingleGate):
    name: Literal[GateName.H] = GateName.H


class XGate(SingleGate):
    name: Literal[GateName.X] = GateName.X


class YGate(SingleGate):
    name: Literal[GateName.Y] = GateName.Y


class ZGate(SingleGate):
    name: Literal[GateName.Z] = GateName.Z


class RotationGate(SingleGate):
    angle: float

    @field_validator("angle")
    @classmethod
    def validate_angle(cls, value: float) -> float:
        return _check_angle(value)


class RxGate(RotationGate):
    name: Literal[GateName.RX] = GateName.RX


class RyGate(RotationGate):
    name: Literal[GateName.RY] = GateName.RY


class RzGate(RotationGate):
    name: Literal[GateName.RZ] = GateName.RZ


class MeasureGate(SingleGate):
    name: Literal[GateName.MEASURE] = GateName.MEASURE
    bit: int

    @field_validator("bit")
    @classmethod
    def validate_bit(cls, value: int) -> int:
        return _check_index(value)


class TwoQubitGate(BaseGate):
    qubit: int
    qubit2: int

    @field_validator("qubit")
    @classmethod
    def validate_qubit(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("qubit2")
    @classmethod
    def validate_qubit2(cls, value: int) -> int:
        return _check_index(value)

    @model_validator(mode="after")
    def validate(self) -> Self:
        _check_indexes(["qubit", "qubit2"], [self.qubit, self.qubit2])
        return self


class SwapGate(TwoQubitGate):
    name: Literal[GateName.SWAP] = GateName.SWAP


class SingleControlledGate(BaseGate):
    control_qubit: int
    target_qubit: int

    @field_validator("control_qubit")
    @classmethod
    def validate_control_qubit(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("target_qubit")
    @classmethod
    def validate_target_qubit(cls, value: int) -> int:
        return _check_index(value)

    @model_validator(mode="after")
    def validate(self) -> Self:
        _check_indexes(["control_qubit", "target_qubit"], [self.control_qubit, self.target_qubit])
        return self


class ChGate(SingleControlledGate):
    name: Literal[GateName.CH] = GateName.CH


class CxGate(SingleControlledGate):
    name: Literal[GateName.CX] = GateName.CX


class CzGate(TwoQubitGate):
    name: Literal[GateName.CZ] = GateName.CZ


class CswapGate(BaseGate):
    name: Literal[GateName.CSWAP] = GateName.CSWAP
    control_qubit: int
    target_qubit: int
    target_qubit2: int

    @field_validator("control_qubit")
    @classmethod
    def validate_control_qubit(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("target_qubit")
    @classmethod
    def validate_target_qubit(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("target_qubit2")
    @classmethod
    def validate_target_qubit2(cls, value: int) -> int:
        return _check_index(value)

    @model_validator(mode="after")
    def validate(self) -> Self:
        _check_indexes(
            ["control_qubit", "target_qubit", "target_qubit2"],
            [self.control_qubit, self.target_qubit, self.target_qubit2],
        )
        return self


class CcxGate(BaseGate):
    name: Literal[GateName.CCX] = GateName.CCX
    control_qubit: int
    control_qubit2: int
    target_qubit: int

    @field_validator("control_qubit")
    @classmethod
    def validate_control_qubit(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("control_qubit2")
    @classmethod
    def validate_control_qubit2(cls, value: int) -> int:
        return _check_index(value)

    @field_validator("target_qubit")
    @classmethod
    def validate_target_qubit(cls, value: int) -> int:
        return _check_index(value)

    @model_validator(mode="after")
    def validate(self) -> Self:
        _check_indexes(
            ["control_qubit", "control_qubit2", "target_qubit"],
            [self.control_qubit, self.control_qubit2, self.target_qubit],
        )
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
        MeasureGate,
        SwapGate,
        ChGate,
        CxGate,
        CzGate,
        CswapGate,
        CcxGate,
    ],
    Field(discriminator="name"),
]

_gate_adapter = TypeAdapter(QuantumGate)
_gates_adapter = TypeAdapter(list[QuantumGate])


def parse_gate(json: Any) -> QuantumGate:
    return _gate_adapter.validate_python(json)


def parse_gates(json: Any) -> list[QuantumGate]:
    return _gates_adapter.validate_python(json)
