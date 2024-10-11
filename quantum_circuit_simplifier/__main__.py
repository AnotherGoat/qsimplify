from networkx.classes import MultiDiGraph
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
import networkx as nx
from quantum_circuit_simplifier.analyzer import analyze
from quantum_circuit_simplifier.model import QuantumMetrics
from quantum_circuit_simplifier.converter import circuit_to_grid, draw_grid, circuit_to_graph

def main():
    circuit = QuantumCircuit(3)

    circuit.h(0)
    circuit.cx(0, 1)
    circuit.h(2)
    circuit.cz(2, 1)
    circuit.t(2)
    circuit.cx(1, 0)
    circuit.ccx(0, 2, 1)
    circuit.x(1)
    circuit.swap(1, 2)
    circuit.z(2)
    circuit.x(1)
    circuit.y(0)
    circuit.cx(0, 1)
    circuit.cswap(0, 1, 2)
    circuit.h(0)
    circuit.ccx(0, 1, 2)
    circuit.h(2)
    circuit.tdg(1)

    print("\n===== Circuit drawing =====")
    print(circuit.draw())

    grid = circuit_to_grid(circuit)
    print("\n===== Circuit grid =====")
    print(draw_grid(grid))

    graph = circuit_to_graph(circuit)
    print("\n===== Circuit graph nodes =====")
    print(graph.nodes(data=True))

    print("\n===== Circuit graph edges =====")
    print(graph.edges(data=True))

    metrics = analyze(circuit)
    print("\n===== Circuit metrics =====")
    print(metrics)

    figure = circuit.draw("mpl")
    #figure.savefig("circuit_diagram.png")

    draw_graph(graph, metrics)


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
    nx.draw_networkx_edges(graph, positions, edgelist=up_edges, node_size=2500, edge_color="red", width=2, connectionstyle="arc3,rad=0.2")

    down_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "down"]
    nx.draw_networkx_edges(graph, positions, edgelist=down_edges, node_size=2500, edge_color="blue", width=2, connectionstyle="arc3,rad=0.2")

    right_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "right"]
    nx.draw_networkx_edges(graph, positions, edgelist=right_edges, node_size=2500, edge_color="green", width=2, connectionstyle="arc3,rad=0.2")

    left_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "left"]
    nx.draw_networkx_edges(graph, positions, edgelist=left_edges, node_size=2500, edge_color="orange", width=2, connectionstyle="arc3,rad=0.2")

    target_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "target"]
    nx.draw_networkx_edges(graph, positions, edgelist=target_edges, node_size=2500, edge_color="purple", width=2, connectionstyle="arc3,rad=0.5")

    target_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["name"] == "controlled_by"]
    nx.draw_networkx_edges(graph, positions, edgelist=target_edges, node_size=2500, edge_color="lightgreen", width=2, connectionstyle="arc3,rad=0.5")

    edge_labels = nx.get_edge_attributes(graph, "name")

    up_labels = {edge: name for edge, name in edge_labels.items() if name == "up"}
    up_label_positions = {node[0]: add_tuples(node[1]["draw_position"], (0.1, 0.05)) for node in graph.nodes(data=True)}
    nx.draw_networkx_edge_labels(graph, up_label_positions, edge_labels=up_labels, rotate=False)

    down_labels = {edge: name for edge, name in edge_labels.items() if name == "down"}
    down_label_positions = {node[0]: add_tuples(node[1]["draw_position"], (-0.1, -0.05)) for node in graph.nodes(data=True)}
    nx.draw_networkx_edge_labels(graph, down_label_positions, edge_labels=down_labels, rotate=False)

    right_labels = {edge: name for edge, name in edge_labels.items() if name == "right"}
    right_label_positions = {node[0]: add_tuples(node[1]["draw_position"], (0.05, -0.1)) for node in graph.nodes(data=True)}
    nx.draw_networkx_edge_labels(graph, right_label_positions, edge_labels=right_labels, rotate=False)

    left_labels = {edge: name for edge, name in edge_labels.items() if name == "left"}
    left_label_positions = {node[0]: add_tuples(node[1]["draw_position"], (-0.05, 0.1)) for node in graph.nodes(data=True)}
    nx.draw_networkx_edge_labels(graph, left_label_positions, edge_labels=left_labels, rotate=False)

    plt.savefig("circuit_graph.png")


if __name__ == "__main__":
    main()
