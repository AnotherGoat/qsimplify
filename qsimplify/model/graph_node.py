from qsimplify.model.gate_name import GateName


class GraphNode:
    """
    Represents a node of a QuantumGraph.

    Attributes:
        name (GateName): The name of quantum gate represented by this node.
        position (Position): The position of this node in the graph.
    """

    def __init__(
        self,
        name: GateName,
        row: int,
        column: int,
        rotation: float | None = None,
        measure_to: int | None = None,
    ):
        if row < 0 or column < 0:
            raise ValueError(
                f"GateNode position '({row}, {column})' can't have negative values"
            )

        self.name = name
        self.position = (row, column)
        self.rotation = rotation
        self.measure_to = measure_to

    def __eq__(self, other) -> bool:
        if not isinstance(other, GraphNode):
            return NotImplemented

        return (
            self.name == other.name
            and self.position == other.position
            and self.rotation == other.rotation
            and self.measure_to == other.measure_to
        )

    def __str__(self):
        rotation_data = f" (rotation={self.rotation})" if self.rotation else ""
        measure_to_data = f" (measure_to={self.measure_to})" if self.measure_to else ""
        return f"{self.name.value} at {self.position}{rotation_data}{measure_to_data}"
