import argparse
from networkx.classes import MultiDiGraph
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
import networkx as nx
from quantum_circuit_simplifier.utils import setup_logger, set_debug_mode
from quantum_circuit_simplifier.model import QuantumMetrics
from quantum_circuit_simplifier.converter import Converter

def main():
    parser = argparse.ArgumentParser(description="Quantum circuit simplifier")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    set_debug_mode(args.debug)

    circuit = QuantumCircuit(3)

    circuit.cx(0, 1)
    circuit.cz(2, 1)
    circuit.ccx(0, 1, 2)
    circuit.h(2)

    #print("\n===== Circuit drawing =====")
    #print(circuit.draw())

    converter = Converter()

    #grid = converter.circuit_to_grid(circuit)
    #print("\n===== Circuit grid =====")
    #print(grid)

    graph = converter.circuit_to_graph(circuit)
    #print("\n===== Circuit graph nodes =====")
    #print(graph.nodes(data=True))

    print("\n===== Circuit graph edges =====")
    #print(graph.edges(data=True))
    print(graph.edges((0,0), data=True))
    print(graph.find_edges(0,0))


    #metrics = analyze(circuit, converter)
    #print("\n===== Circuit metrics =====")
    #print(metrics)

    figure = circuit.draw("mpl")
    #figure.savefig("circuit_diagram.png")

    #draw_graph(graph, metrics)


def add_tuples(tuple1: tuple[float, float], tuple2: tuple[float, float]) -> tuple[float, float]:
    return tuple1[0] + tuple2[0], tuple1[1] + tuple2[1]


def draw_graph(graph: MultiDiGraph, metrics: QuantumMetrics):
    plt.clf()
    plt.figure(figsize=(2.75 * metrics.depth, 2 * metrics.width))

    positions = {node[0]:node[1]["draw_position"] for node in graph.nodes(data=True)}
    nx.draw_networkx_nodes(graph, pos=positions, node_size=2500, node_color="lightgray")

    labels = {node[0]:node[1]["name"] for node in graph.nodes(data=True)}
    nx.draw_networkx_labels(graph, pos=positions, labels=labels)

    up_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "up"]
    nx.draw_networkx_edges(graph, positions, edgelist=up_edges, node_size=2500, edge_color="red", width=2, connectionstyle="arc3,rad=0.15")

    down_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "down"]
    nx.draw_networkx_edges(graph, positions, edgelist=down_edges, node_size=2500, edge_color="blue", width=2, connectionstyle="arc3,rad=0.15")

    right_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "right"]
    nx.draw_networkx_edges(graph, positions, edgelist=right_edges, node_size=2500, edge_color="green", width=2, connectionstyle="arc3,rad=0.15")

    left_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "left"]
    nx.draw_networkx_edges(graph, positions, edgelist=left_edges, node_size=2500, edge_color="orange", width=2, connectionstyle="arc3,rad=0.15")

    target_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "target"]
    nx.draw_networkx_edges(graph, positions, edgelist=target_edges, node_size=2500, edge_color="purple", width=2, connectionstyle="arc3,rad=0.3")

    target_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "controlled_by"]
    nx.draw_networkx_edges(graph, positions, edgelist=target_edges, node_size=2500, edge_color="lightgreen", width=2, connectionstyle="arc3,rad=0.3")

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
    plt.savefig("circuit_graph.png")


if __name__ == "__main__":
    main()
