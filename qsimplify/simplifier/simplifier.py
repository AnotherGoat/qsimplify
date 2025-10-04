"""Contains the quantum circuit simplifier."""

from pathlib import Path

from qsimplify.model import QuantumGraph, graph_cleaner
from qsimplify.simplifier.pattern_replacement_rule import PatternReplacementRule
from qsimplify.simplifier.rule_parser import RuleParser


class Simplifier:
    """Simplifies a quantum graph using a set of rules."""

    _default_rules: list[PatternReplacementRule]

    def __init__(self) -> None:
        """Create a new simplifier."""
        parser = RuleParser()
        script_path = Path(__file__).parent
        default_rules_path = script_path / "default_rules.json"

        self._default_rules = parser.load_rules_from_file(default_rules_path)

    def simplify_graph(
        self,
        graph: QuantumGraph,
        rules: list[PatternReplacementRule] | None = None,
        iterations: int = 1,
    ) -> QuantumGraph:
        """Simplify a quantum graph using a set of rules.

        A custom set of rules can be provided. If not, the default rules will be used.
        The graph will be cleaned up after applying all the rules.
        """
        if iterations <= 0:
            raise ValueError("Number of iterations must be greater than 0")

        if rules is None:
            rules = self._default_rules

        result = graph.copy()

        for _ in range(iterations):
            for rule in rules:
                rule.apply(result)

            graph_cleaner.clean_and_fill(result)

        return result
