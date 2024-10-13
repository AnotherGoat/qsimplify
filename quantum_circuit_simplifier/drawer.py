import matplotlib.pyplot as plt
import networkx as nx
from qiskit import QuantumCircuit

from quantum_circuit_simplifier.model import QuantumGraph, QuantumMetrics
from quantum_circuit_simplifier.utils import setup_logger


class Drawer:
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
        plt.figure(figsize=(2.75 * graph.width, 2 * graph.height))

        positions = {node[0]: node[1]["draw_position"] for node in graph.nodes(data=True)}
        nx.draw_networkx_nodes(graph, pos=positions, node_size=2500, node_color="lightgray")

        labels = {node[0]: node[1]["name"] for node in graph.nodes(data=True)}
        nx.draw_networkx_labels(graph, pos=positions, labels=labels)

        up_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "up"]
        nx.draw_networkx_edges(graph, positions, edgelist=up_edges, node_size=2500, edge_color="red", width=2,
                               connectionstyle="arc3,rad=0.15")

        down_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "down"]
        nx.draw_networkx_edges(graph, positions, edgelist=down_edges, node_size=2500, edge_color="blue", width=2,
                               connectionstyle="arc3,rad=0.15")

        right_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "right"]
        nx.draw_networkx_edges(graph, positions, edgelist=right_edges, node_size=2500, edge_color="green", width=2,
                               connectionstyle="arc3,rad=0.15")

        left_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "left"]
        nx.draw_networkx_edges(graph, positions, edgelist=left_edges, node_size=2500, edge_color="orange", width=2,
                               connectionstyle="arc3,rad=0.15")

        target_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "target"]
        nx.draw_networkx_edges(graph, positions, edgelist=target_edges, node_size=2500, edge_color="purple", width=2,
                               connectionstyle="arc3,rad=0.3")

        target_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "controlled_by"]
        nx.draw_networkx_edges(graph, positions, edgelist=target_edges, node_size=2500, edge_color="lightgreen",
                               width=2, connectionstyle="arc3,rad=0.3")

        legend_handles = [
            plt.Line2D([0], [0], color="red", lw=2, label="Up"),
            plt.Line2D([0], [0], color="blue", lw=2, label="Down"),
            plt.Line2D([0], [0], color="green", lw=2, label="Right"),
            plt.Line2D([0], [0], color="orange", lw=2, label="Left"),
            plt.Line2D([0], [0], color="purple", lw=2, label="Target"),
            plt.Line2D([0], [0], color="lightgreen", lw=2, label="Controlled by"),
        ]

        plt.legend(handles=legend_handles, loc="upper left")
        plt.tight_layout()
        plt.savefig(file_name)
