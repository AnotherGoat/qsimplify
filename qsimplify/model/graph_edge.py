"""Contains the graph edge view data structure."""

from dataclasses import dataclass

from qsimplify.model.edge_name import EdgeName
from qsimplify.model.graph_node import GraphNode


@dataclass(frozen=True)
class GraphEdge:
    """A view of an edge in a quantum graph."""

    name: EdgeName
    """The name of the edge."""
    start: GraphNode
    """The node at the start of the edge."""
    end: GraphNode
    """The node at the end of the edge."""

    def __str__(self) -> str:
        """Get a string representation of this view."""
        return f"[{self.name.value}] from {self.start} to {self.end}"
