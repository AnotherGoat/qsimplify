from enum import Enum


class EdgeName(Enum):
    LEFT = "left"
    RIGHT = "right"
    SWAPS_WITH = "swaps_with"
    TARGETS = "targets"
    CONTROLLED_BY = "controlled_by"
    WORKS_WITH = "works_with"

    def is_positional(self) -> bool:
        return self in (EdgeName.LEFT, EdgeName.RIGHT)
