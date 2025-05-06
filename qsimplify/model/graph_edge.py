from dataclasses import dataclass

from qsimplify.model.edge_name import EdgeName
from qsimplify.model.graph_node import GraphNode


@dataclass(frozen=True)
class GraphEdge:
    """A view of an edge in a quantum graph.

    Attributes:
        name: The name of the edge.
        start: The node at the start of the edge.
        end: The node at the end of the edge.

    """

    name: EdgeName
    start: GraphNode
    end: GraphNode

    def __str__(self) -> str:
        """Get a string representation of this view."""
        return f"[{self.name.value}] from {self.start} to {self.end}"
