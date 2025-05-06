from dataclasses import dataclass, field

from qsimplify.model.graph_node import GraphNode


@dataclass(frozen=True)
class EdgeData:
    """A view of a node in a quantum graph, including all the nodes in the edges connected to it.

    Attributes:
        origin: The node at the center of the view.
        left: The node at the left of the origin node.
        right: The node at the right of the origin node.
        swaps_with: The node that is swapped with the origin node.
        targets: The nodes that are targeted by the origin node.
        controlled_by: The nodes that control the origin node.
        works_with: The nodes that work together with the origin node.

    """

    origin: GraphNode
    left: GraphNode | None = None
    right: GraphNode | None = None
    swaps_with: GraphNode | None = None
    targets: list[GraphNode] = field(default_factory=list)
    controlled_by: list[GraphNode] = field(default_factory=list)
    works_with: list[GraphNode] = field(default_factory=list)

    def __str__(self) -> str:
        """Get a string representation of this view."""
        target_names = [str(target) for target in self.targets]
        controller_names = [str(controller) for controller in self.controlled_by]
        works_with_names = [str(controller) for controller in self.works_with]
        extra_data = [
            f"left={self.left}" if self.left else "",
            f"right={self.right}" if self.right else "",
            f"swaps_with={self.swaps_with}" if self.swaps_with else "",
            f"targets={target_names}" if target_names else "",
            f"controlled_by={controller_names}" if controller_names else "",
            f"works_with={works_with_names}" if works_with_names else "",
        ]
        extra_data = [data for data in extra_data if data]

        if len(extra_data) == 0:
            return str(self.origin)

        return f"{self.origin}({', '.join(extra_data)})"
