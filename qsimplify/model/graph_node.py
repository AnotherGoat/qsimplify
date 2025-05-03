from dataclasses import dataclass

from qsimplify.model.gate_name import GateName
from qsimplify.model.position import Position


@dataclass(frozen=True)
class GraphNode:
    """
    A view of a node in a quantum graph.

    Attributes:
        name: The name of quantum gate represented by this node.
        position: The position of this node in the graph.
        rotation: The rotation angle attached to this node, only for rotation gates.
        measure_to: The classical bit where the measured qubit is stored, only for measure gates.
    """

    name: GateName
    position: Position
    rotation: float | None = None
    measure_to: int | None = None

    def __str__(self) -> str:
        """Get a string representation of this view."""
        rotation_data = f" (rotation={self.rotation})" if self.rotation else ""
        measure_to_data = f" (measure_to={self.measure_to})" if self.measure_to else ""
        return f"{self.name.value} at {self.position}{rotation_data}{measure_to_data}"
