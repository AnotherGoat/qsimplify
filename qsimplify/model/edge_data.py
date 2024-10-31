from qsimplify.model.graph_node import GraphNode

class EdgeData:
    def __init__(
        self,
        origin: GraphNode,
        left: GraphNode | None = None,
        right: GraphNode | None = None,
        swaps_with: GraphNode | None = None,
        targets: list[GraphNode] | None = None,
        controlled_by: list[GraphNode] | None = None,
        works_with: list[GraphNode] | None = None,
    ):
        self.origin = origin
        self.left = left
        self.right = right
        self.swaps_with = swaps_with
        self.targets = targets if targets is not None else []
        self.controlled_by = controlled_by if controlled_by is not None else []
        self.works_with = works_with if works_with is not None else []

    def __str__(self) -> str:
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
