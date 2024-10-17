from qiskit import QuantumCircuit

from quantum_circuit_simplifier.converter import Converter
from quantum_circuit_simplifier.model import QuantumGraph, GraphNode, GateName

_RULES = {}

class Simplifier:
    def __init__(self, converter: Converter):
        self.converter = converter

    def simplify_circuit(self, circuit: QuantumCircuit) -> QuantumCircuit:
        graph = self.converter.circuit_to_graph(circuit)
        simplified_graph = self.simplify_graph(graph)
        return self.converter.graph_to_circuit(simplified_graph)

    def simplify_graph(self, graph: QuantumGraph) -> QuantumGraph:
        result = QuantumGraph()
        result.network = graph.network.copy()

        matches = True

        while matches:
            matches = False

            for position in result.get_positions():
                node = result[position]

                if self._remove_duplicate_h(result, node):
                    matches = True
                    break

        return result

    @staticmethod
    def _remove_duplicate_h(graph: QuantumGraph, node: GraphNode) -> bool:
        if node.name != GateName.H:
            return False

        start = node.position
        edges = graph.find_edges(*start)
        right_edge = edges.right

        if right_edge and right_edge.name == GateName.H:
            graph.add_node(GraphNode(GateName.ID, start))
            graph.add_node(GraphNode(GateName.ID, right_edge.position))
            return True

        return False
