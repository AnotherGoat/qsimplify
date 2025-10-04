from typing import override

from loguru import logger

from qsimplify.model import GateName, QuantumGraph, graph_cleaner
from qsimplify.simplifier import pattern_matcher, pattern_replacer
from qsimplify.simplifier.position_mask import PositionMask
from qsimplify.simplifier.quantum_pattern import QuantumPattern
from qsimplify.simplifier.simplification_rule import SimplificationRule


class PatternReplacementRule(SimplificationRule):
    """A rule for simplifying a quantum graph, by replacing a pattern."""

    original: QuantumPattern
    replacement: QuantumGraph
    mask: PositionMask

    def __init__(self, original: QuantumPattern, replacement: QuantumGraph) -> None:
        """Create a new simplification rule.

        The replacement is usually expected to be smaller than the original pattern, and this rule may not work if this is not true.
        """
        self.original = original
        self.replacement = replacement
        self._fill_replacement()
        self._generate_mask()

    def _fill_replacement(self) -> None:
        """Add extra identity gates to the replacement graph, to make it match the original pattern in size."""
        for position in self.original.iter_positions_by_row():
            if not self.replacement.has_node_at(position):
                self.replacement.add_node(GateName.ID, position)

        graph_cleaner.fill(self.replacement)

    def _generate_mask(self) -> None:
        """Generate a mask that indicates the positions that should be taken into account when doing the replacement."""
        self.mask = PositionMask(
            {node.position: node.name != GateName.ID for node in self.replacement}
        )

    @override
    def __str__(self) -> str:
        """Get a string representation of this rule."""
        return f"Replace\n{self.original.draw_grid()}\nWith\n{self.replacement.draw_grid()}"

    @override
    def apply(self, graph: QuantumGraph) -> None:
        """Apply this pattern-based simplification rule to a graph."""
        logger.debug("Applying simplification rule with mask {}", self.mask)

        while match := pattern_matcher.match_pattern(self.original, graph, self.mask):
            before = graph.copy()
            pattern_replacer.replace_pattern(graph, self.replacement, match)

            if graph == before:
                logger.info("Replacement made no changes, stopping early")
                break
