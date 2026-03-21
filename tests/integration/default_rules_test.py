from pathlib import Path

from qsimplify.analyzer import matrix_calculator
from qsimplify.simplifier import RuleParser


def test_default_rules():
    parser = RuleParser()
    root = Path(__file__).parent.parent.parent
    default_rules_path = root / "qsimplify" / "simplifier" / "default_rules.json"

    rules = parser.load_rules_from_file(default_rules_path)

    for rule in rules:
        matrix_calculator.are_graphs_equivalent(rule.original, rule.replacement)
