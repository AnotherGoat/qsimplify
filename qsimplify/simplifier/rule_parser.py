"""Contains the rule parser.."""

import json
from pathlib import Path

from qsimplify.converter.gates_converter import GatesConverter
from qsimplify.model.quantum_gate import parse_gates
from qsimplify.simplifier.simplification_rule import SimplificationRule

GATES_CONVERTER = GatesConverter()


class RuleParser:
    """A parser that can load a set of simplification rules from JSON data."""

    def load_rules_from_file(self, path: Path) -> list[SimplificationRule]:
        """Load simplification rules from the specified JSON file."""
        with path.open("r") as file:
            json_data = json.load(file)

        return self._parse_rules(json_data)

    def load_rules(self, json_text: str) -> list[SimplificationRule]:
        """Load simplification rules from the specified JSON file contents, as plain text."""
        json_data = json.loads(json_text)
        return self._parse_rules(json_data)

    def _parse_rules(self, json_data: list[dict]) -> list[SimplificationRule]:
        return [self._parse_rule(rule_data) for rule_data in json_data]

    def _parse_rule(self, rule_data: dict) -> SimplificationRule | None:
        if "pattern" not in rule_data or "replacement" not in rule_data:
            raise ValueError(f"The rule {rule_data} is missing its pattern or replacement keys")

        pattern_gates = parse_gates(rule_data["pattern"])
        pattern = GATES_CONVERTER.to_graph(pattern_gates, False)

        replacement_gates = parse_gates(rule_data["replacement"])
        replacement = GATES_CONVERTER.to_graph(replacement_gates, False)

        return SimplificationRule(pattern, replacement)
