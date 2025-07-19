from qsimplify.model import GraphBuilder, Position
from qsimplify.simplifier import SimplificationRule
from qsimplify.simplifier.simplification_rule import PositionMask


def test_position_mask():
    pattern = GraphBuilder().push_x(0).push_y(0).build()
    replacement = GraphBuilder().push_x(0).put_y(0, 3).build(False)

    rule = SimplificationRule(pattern, replacement)

    expected = PositionMask(
        {
            Position(0, 0): True,
            Position(0, 1): False,
            Position(0, 2): False,
            Position(0, 3): True,
        }
    )

    assert rule.mask == expected
