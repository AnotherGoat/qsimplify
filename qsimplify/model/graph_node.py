from dataclasses import dataclass

from qsimplify.model.gate_name import GateName
from qsimplify.model.position import Position


@dataclass(frozen=True)
class GraphNode:
    """A view of a node in a quantum graph.

    Attributes:
        name: The name of quantum gate represented by this node.
        position: The position of this node in the graph.
        angle: The rotation angle attached to this node, only for rotation gates.
        bit: The classical bit where the measured qubit is stored, only for measure gates.

    """

    name: GateName
    position: Position
    angle: float | None = None
    bit: int | None = None

    def __str__(self) -> str:
        """Get a string representation of this view."""
        angle_data = f" (angle={self.angle})" if self.angle else ""
        bit_data = f" (bit={self.bit})" if self.bit else ""
        return f"{self.name.value} at {self.position}{angle_data}{bit_data}"
