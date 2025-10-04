"""Contains the rule parser.."""

import json
from pathlib import Path
from typing import Any

from qsimplify.converter.gates_converter import GatesConverter
from qsimplify.model.quantum_gate import parse_gates
from qsimplify.simplifier.pattern_replacement_rule import PatternReplacementRule
from qsimplify.simplifier.quantum_pattern import QuantumPattern

GATES_CONVERTER = GatesConverter()


class RuleParser:
    """A parser that can load a set of pattern replacement rules from JSON data."""

    def load_rules_from_file(self, path: Path) -> list[PatternReplacementRule]:
        """Load simplification rules from the specified JSON file."""
        with path.open("r") as file:
            json_data = json.load(file)

        return self._parse_rules(json_data)

    def load_rules(self, json_text: str) -> list[PatternReplacementRule]:
        """Load simplification rules from the specified JSON file contents, as plain text."""
        json_data = json.loads(json_text)
        return self._parse_rules(json_data)

    def _parse_rules(self, json_data: list[dict]) -> list[PatternReplacementRule]:
        return [self._parse_rule(rule_data) for rule_data in json_data]

    @staticmethod
    def _parse_rule(rule_data: dict[str, Any]) -> PatternReplacementRule | None:
        if "original" not in rule_data or "replacement" not in rule_data:
            raise ValueError(f"The rule {rule_data} is missing its original or replacement keys")

        original_gates = parse_gates(rule_data["original"])
        original = GATES_CONVERTER.to_graph(original_gates, False)

        replacement_gates = parse_gates(rule_data["replacement"])
        replacement = GATES_CONVERTER.to_graph(replacement_gates, False)

        return PatternReplacementRule(QuantumPattern(original), replacement)
