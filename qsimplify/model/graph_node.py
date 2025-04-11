from dataclasses import dataclass

from qsimplify.model.gate_name import GateName
from qsimplify.model.position import Position


@dataclass(frozen=True)
class GraphNode:
    """
    Represents a node of a QuantumGraph.

    Attributes:
        name (GateName): The name of quantum gate represented by this node.
        position (Position): The position of this node in the graph.
    """

    name: GateName
    position: Position
    rotation: float | None = None
    measure_to: int | None = None

    def __str__(self) -> str:
        rotation_data = f" (rotation={self.rotation})" if self.rotation else ""
        measure_to_data = f" (measure_to={self.measure_to})" if self.measure_to else ""
        return f"{self.name.value} at {self.position}{rotation_data}{measure_to_data}"
