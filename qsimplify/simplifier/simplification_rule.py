"""Contains the base for subgraph-based simplification rules."""

import itertools
from abc import ABC, abstractmethod
from typing import assert_never, override

from loguru import logger

from qsimplify import math_utils
from qsimplify.model import GateName, QuantumGraph, graph_cleaner
from qsimplify.model.graph_node import GraphNode
from qsimplify.model.position import Position
from qsimplify.simplifier import QuantumPattern
from qsimplify.simplifier.pattern_match import PatternMatch


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
