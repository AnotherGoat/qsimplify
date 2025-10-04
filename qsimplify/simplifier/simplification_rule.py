"""Contains the base for subgraph-based simplification rules."""

from abc import ABC, abstractmethod
from typing import override

from qsimplify.model import QuantumGraph


class SimplificationRule(ABC):
    """A generic rule for simplifying quantum graphs."""

    @abstractmethod
    def apply(self, graph: QuantumGraph) -> None:
        """Apply this rule to a graph."""


class AngleSimplificationRule(SimplificationRule):
    """A rule for simplifying a quantum graph, by merging adjacent angles."""

    @override
    def apply(self, graph: QuantumGraph) -> None:
        pass
