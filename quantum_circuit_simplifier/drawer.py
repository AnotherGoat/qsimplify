import matplotlib.pyplot as plt
import networkx as nx
from qiskit import QuantumCircuit

from quantum_circuit_simplifier.model import QuantumGraph, Position, GraphNode
from quantum_circuit_simplifier.utils import setup_logger

class EdgeType:
    def __init__(self, name: str, color: str, angle: float):
        self.name = name
        self.color = color
        self.angle = angle

class Drawer:
    _NODE_COLOR = "lightgray"
    _NODE_SIZE = 5000
    _LINE_WIDTH = 2
    _EDGE_TYPES = [
        EdgeType("up", "red", 0.15),
        EdgeType("down", "blue", 0.15),
        EdgeType("right", "green", 0.15),
        EdgeType("left", "orange", 0.15),
        EdgeType("targets", "purple", 0.3),
        EdgeType("controlled_by", "lightgreen", 0.3),
    ]

    def __init__(self):
        self.logger = setup_logger("Drawer")

    def save_circuit(self, circuit: QuantumCircuit, file_name: str):
        self.logger.info("Saving circuit to file %s", file_name)

        plt.clf()
        figure = circuit.draw("mpl")
        figure.savefig(file_name)


    def save_graph(self, graph: QuantumGraph, file_name: str):
        self.logger.info("Saving graph to file %s", file_name)
        plt.clf()
        plt.figure(figsize=(3 * graph.width, 2.5 * graph.height))

        self._draw_nodes(graph)

        for edge_type in self._EDGE_TYPES:
            self._draw_edges(edge_type, graph)

        self._draw_legend()

        plt.tight_layout()
        plt.savefig(file_name)

    def _draw_nodes(self, graph: QuantumGraph):
        draw_positions = self._find_draw_positions(graph)

        nx.draw_networkx_nodes(graph.network, pos=draw_positions, node_size=self._NODE_SIZE, node_color=self._NODE_COLOR)

        labels = {node.position: str(node) for node in graph.get_gate_nodes()}
        nx.draw_networkx_labels(graph.network, pos=draw_positions, labels=labels)


    @staticmethod
    def _find_draw_positions(graph) -> dict[Position, Position]:
        return {position: (position[1], graph.height - position[0] - 1) for position in graph.get_positions()}


    def _draw_edges(self, edge_type: EdgeType, graph: QuantumGraph):
        draw_positions = self._find_draw_positions(graph)

        edges = [(edge.start.position, edge.end.position) for edge in graph.get_edges() if edge.name == edge_type.name]
        nx.draw_networkx_edges(graph.network, draw_positions, edgelist=edges, node_size=self._NODE_SIZE, edge_color=edge_type.color,
                               width=self._LINE_WIDTH, connectionstyle=f"arc3,rad={edge_type.angle}")

    def _draw_legend(self):
        legend_handles = [self._create_legend_handle(edge_type) for edge_type in self._EDGE_TYPES]
        plt.legend(handles=legend_handles, loc="upper left")


    def _create_legend_handle(self, edge_type: EdgeType) -> plt.Line2D:
        return plt.Line2D([0], [0], color=edge_type.color, lw=self._LINE_WIDTH, label=edge_type.name)
