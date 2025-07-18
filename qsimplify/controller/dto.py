"""Contains data transfer objects only used by the REST API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from qsimplify.analyzer.metrics import DeltaMetrics, Metrics
from qsimplify.model import quantum_gate
from qsimplify.model.quantum_gate import QuantumGate


class MessageResponse(BaseModel):
    """A generic message response, which can be an error or a success."""

    message: str


class ErrorList(BaseModel):
    """A generic list of error messages."""

    errors: list[str]


class GateList(BaseModel):
    """A list of quantum gates."""

    gates: list[QuantumGate]
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _parse_gates(cls, values: dict[str, Any]) -> dict[str, Any]:
        raw_gates = values.get("gates")

        if raw_gates is not None:
            values["gates"] = quantum_gate.parse_gates(raw_gates)

        return values


class SimplificationRequest(GateList):
    """A request to simplify a quantum circuit."""

    iterations: int = 1

    @field_validator("iterations")
    @classmethod
    def _validate_iterations(cls, value: int) -> int:
        if value < 1:
            raise ValueError("It must be positive")

        return value


class GateListErrors(BaseModel):
    """Error messages for a failed validation of a list of gates."""

    errors: dict[int, list[str]]


class SimplifiedCircuit(BaseModel):
    """The result after a quantum circuit is simplified."""

    gates: GateList
    original_metrics: Metrics
    new_metrics: Metrics
    delta_metrics: DeltaMetrics
    code: str


class PlottingRequest(GateList):
    """A request to plot a quantum circuit."""

    dpi: int = 96

    @field_validator("dpi")
    @classmethod
    def _validate_dpi(cls, value: int) -> int:
        if value < 72 or value > 300:
            raise ValueError("It must be a value between 72 and 300")

        return value


class GeneratedCode(BaseModel):
    """Generated code for building a quantum circuit."""

    code: str


class MetricsResult(BaseModel):
    """Metrics calculated for a quantum circuit."""

    metrics: Metrics


class GatesToCompare(BaseModel):
    """A pair of quantum circuits to compare."""

    old_gates: list[QuantumGate]
    new_gates: list[QuantumGate]
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _parse_gates(cls, values: dict[str, Any]) -> dict[str, Any]:
        raw_old_gates = values.get("old_gates")

        if raw_old_gates is not None:
            values["old_gates"] = quantum_gate.parse_gates(raw_old_gates)

        raw_new_gates = values.get("new_gates")

        if raw_new_gates is not None:
            values["new_gates"] = quantum_gate.parse_gates(raw_new_gates)

        return values


class DeltaMetricsResult(BaseModel):
    """Difference in metrics between two quantum circuits."""

    delta_metrics: DeltaMetrics
