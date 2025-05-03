from enum import Enum


class EdgeName(Enum):
    """The types of edges between graph nodes."""

    LEFT = "left"
    """An edge that goes from the starting node to the node on its left. It's always paired with an opposite RIGHT edge."""
    RIGHT = "right"
    """An edge that goes from the starting node to the node on its right. It's always paired with an opposite LEFT edge."""
    SWAPS_WITH = "swaps_with"
    """Connects two nodes that are swapped with each other in SWAP and CSWAP gates. It's always bidirectional."""
    TARGETS = "targets"
    """Connects the starting node (controller) with a node that it targets. It's always paired with an opposite CONTROLLED_BY edge."""
    CONTROLLED_BY = "controlled_by"
    """Connects the starting node (target) with a node that controls it. It's always paired with an opposite TARGETS edge."""
    WORKS_WITH = "works_with"
    """Connects controller nodes that work together. Also connects every node in CZ and CCZ gates. It's always bidirectional."""

    def is_positional(self) -> bool:
        """Check whether this edge is related to the node's position or not."""
        return self in (EdgeName.LEFT, EdgeName.RIGHT)
