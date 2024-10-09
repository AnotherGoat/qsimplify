from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
import networkx as nx

from quantum_circuit_simplifier.analyzer import analyze
from quantum_circuit_simplifier.converter import circuit_to_grid, draw_grid, circuit_to_graph


def make_graph_label(label: str) -> str:
    match label:
        case "left" | "right":
            return "left-right"
        case "up" | "down":
            return "up-down"
        case _:
            return "related"


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
    figure.savefig("circuit_diagram.png")

    plt.clf()
    plt.figure(figsize=(2 * metrics.depth, 1.5 * metrics.width))

    positions = {node[0]:node[1]["draw_position"] for node in graph.nodes(data=True)}
    labels = nx.get_node_attributes(graph, "name")
    nx.draw(graph, pos=positions, with_labels=True, labels=labels, node_size=2500, node_color="lightgreen", font_weight="bold")

    edge_labels = nx.get_edge_attributes(graph, "name")
    edge_labels = {key: make_graph_label(label) for key, label in edge_labels.items()}
    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels)

    plt.savefig("circuit_graph.png")


if __name__ == "__main__":
    main()
