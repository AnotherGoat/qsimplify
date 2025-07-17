"""Contains data transfer objects only used by the REST API."""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, model_validator

from qsimplify.analyzer.metrics import DeltaMetrics, Metrics
from qsimplify.model import quantum_gate
from qsimplify.model.quantum_gate import QuantumGate


@dataclass(frozen=True)
class MessageResponse:
    """A generic message response."""

    message: str


@dataclass(frozen=True)
class GateList(BaseModel):
    """A list of quantum gates."""

    gates: list[QuantumGate]

    @model_validator(mode="before")
    @classmethod
    def _parse_gates(cls, values: dict[str, Any]) -> dict[str, Any]:
        raw_gates = values.get("gates", [])
        values["gates"] = quantum_gate.parse_gates(raw_gates)
        return values


@dataclass(frozen=True)
class SimplifiedCircuit:
    """The result after a quantum circuit is simplified."""

    gates: GateList
    original_metrics: Metrics
    new_metrics: Metrics
    delta_metrics: DeltaMetrics
    code: str


@dataclass(frozen=True)
class GeneratedCode:
    """Generated code for building a quantum circuit."""

    code: str


@dataclass(frozen=True)
class MetricsResult:
    """Metrics calculated for a quantum circuit."""

    metrics: Metrics


@dataclass(frozen=True)
class GatesToCompare(BaseModel):
    """A pair of quantum circuits to compare."""

    old_gates: list[QuantumGate]
    new_gates: list[QuantumGate]

    @model_validator(mode="before")
    @classmethod
    def _parse_gates(cls, values: dict[str, Any]) -> dict[str, Any]:
        raw_old_gates = values.get("old_gates", [])
        values["old_gates"] = quantum_gate.parse_gates(raw_old_gates)

        raw_new_gates = values.get("new_gates", [])
        values["new_gates"] = quantum_gate.parse_gates(raw_new_gates)

        return values


@dataclass(frozen=True)
class DeltaMetricsResult:
    """Difference in metrics between two quantum circuits."""

    delta_metrics: DeltaMetrics
