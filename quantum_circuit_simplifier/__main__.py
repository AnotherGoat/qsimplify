from matplotlib.collections import PatchCollection
from networkx.classes import DiGraph
from qiskit import QuantumCircuit
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
from quantum_circuit_simplifier.converter import circuit_to_graph, circuit_to_grid, draw_grid


def main():
    circuit = QuantumCircuit(3)

    circuit.cx(0, 1)
    circuit.cz(2, 1)
    circuit.cx(0, 1)
    circuit.cz(2, 1)
    circuit.cx(0, 1)
    circuit.cz(2, 1)
    circuit.cx(0, 1)
    circuit.cz(2, 1)
    circuit.cx(0, 1)
    circuit.cz(2, 1)
    circuit.cx(0, 1)
    circuit.cz(2, 1)
    circuit.h(0)
    circuit.ccx(0, 1, 2)
    circuit.h(2)

    print(circuit.draw())
    grid = circuit_to_grid(circuit)
    print(draw_grid(grid))

    figure = circuit.draw("mpl")
    # figure.savefig("circuit_diagram.png")

    plt.clf()

    graph = DiGraph()
    graph.add_node(1)
    graph.add_node(2)

    graph.add_edge(1, 2, name="right")
    graph.add_edge(2, 1, name="left")

    print(graph.nodes(data=True))
    print(graph.edges(data=True))
    print(graph.out_edges(1, data=True))
    print(graph.out_edges(2, data=True))



    # Draw the graph
    plt.figure(figsize=(8, 6))

    # Draw nodes and edges
    pos = nx.spring_layout(graph)  # Positions for all nodes
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=16, font_color='black',
            font_weight='bold', arrows=True)

    nx.draw_networkx_edges(graph, pos, edgelist=[(1, 2)], connectionstyle="arc3,rad=0.2", arrowstyle='-|>',
                           edge_color='black')
    nx.draw_networkx_edges(graph, pos, edgelist=[(2, 1)], connectionstyle="arc3,rad=-0.2", arrowstyle='-|>',
                           edge_color='black')

    # Draw edge labels (to show the edge name like "right" and "left")
    edge_labels = {(1, 2): 'right', (2, 1): 'left'}
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, label_pos=0.6, font_size=12, font_color='black')

    #edge_labels = nx.get_edge_attributes(graph, 'name')
    #nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    # Display the graph
    #plt.savefig("circuit_graph.png")





    #graph = circuit_to_graph(circuit)
    #print("\n".join([str(gate) for gate in graph.gates()]))



if __name__ == "__main__":
    main()
