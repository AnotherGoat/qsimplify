from qsimplify.model.edge_name import EdgeName
from qsimplify.model.graph_node import GraphNode


class GraphEdge:
    def __init__(self, name: EdgeName, start: GraphNode, end: GraphNode):
        self.name = name
        self.start = start
        self.end = end

    def __eq__(self, other) -> bool:
        if not isinstance(other, GraphEdge):
            return NotImplemented

        return self.name == other.name and self.start == other.start and self.end == other.end


    def __str__(self):
        return f"[{self.name.value}] from {self.start} to {self.end}"
