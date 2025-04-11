from dataclasses import dataclass

from qsimplify.model.edge_name import EdgeName
from qsimplify.model.graph_node import GraphNode


@dataclass(frozen=True)
class GraphEdge:
    name: EdgeName
    start: GraphNode
    end: GraphNode

    def __str__(self) -> str:
        return f"[{self.name.value}] from {self.start} to {self.end}"
