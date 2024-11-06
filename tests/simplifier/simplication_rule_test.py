from qsimplify.model import GraphBuilder
from qsimplify.simplifier import SimplificationRule


def test_rule_mask():
    pattern = GraphBuilder().add_x(0, 0).add_y(0, 1).build()
    replacement = GraphBuilder().add_x(0, 0).add_y(0, 3).build()

    rule = SimplificationRule(pattern, replacement)

    expected = {
        (0, 0): True,
        (0, 1): False,
        (0, 2): False,
        (0, 3): True,
    }

    assert rule.mask == expected
