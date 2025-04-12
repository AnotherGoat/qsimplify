from qsimplify.model import GraphBuilder, Position
from qsimplify.simplifier import SimplificationRule


def test_rule_mask():
    pattern = GraphBuilder().add_x(0, 0).add_y(0, 1).build(clean_up=False)
    replacement = GraphBuilder().add_x(0, 0).add_y(0, 3).build(clean_up=False)

    rule = SimplificationRule(pattern, replacement)

    expected = {
        Position(0, 0): True,
        Position(0, 1): False,
        Position(0, 2): False,
        Position(0, 3): True,
    }

    assert rule.mask == expected
