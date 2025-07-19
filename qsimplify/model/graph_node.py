"""Contains the graph node view data structure."""

from dataclasses import dataclass

from qsimplify.model.gate_name import GateName
from qsimplify.model.position import Position


@dataclass(frozen=True)
class GraphNode:
    """A view of a node in a quantum graph."""

    name: GateName
    """The name of quantum gate represented by this node."""
    position: Position
    """The position of this node in the graph."""
    angle: float | None = None
    """The rotation angle attached to this node, only for rotation gates."""
    bit: int | None = None
    """The classical bit where the measured qubit is stored, only for measure gates."""

    def __str__(self) -> str:
        """Get a string representation of this view."""
        angle_data = f" (angle={self.angle})" if self.angle else ""
        bit_data = f" (bit={self.bit})" if self.bit else ""
        return f"{self.name.value} at {self.position}{angle_data}{bit_data}"
