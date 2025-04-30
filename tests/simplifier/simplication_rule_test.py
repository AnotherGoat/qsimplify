from qsimplify.model import GraphBuilder, Position
from qsimplify.simplifier import SimplificationRule


def test_rule_mask():
    pattern = GraphBuilder().push_x(0).push_y(0).build()
    replacement = GraphBuilder().push_x(0).put_y(0, 3).build(False)

    rule = SimplificationRule(pattern, replacement)

    expected = {
        Position(0, 0): True,
        Position(0, 1): False,
        Position(0, 2): False,
        Position(0, 3): True,
    }

    assert rule.mask == expected
