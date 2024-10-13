import argparse

from qiskit import QuantumCircuit

from quantum_circuit_simplifier.drawer import Drawer
from quantum_circuit_simplifier.utils import set_debug_mode
from quantum_circuit_simplifier.converter import Converter


def _main():
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

    #print("\n===== Circuit graph edges =====")
    #print(graph.edges(data=True))

    #metrics = analyze(circuit, converter)
    #print("\n===== Circuit metrics =====")
    #print(metrics)

    drawer = Drawer()
    #drawer.save_circuit(circuit, "circuit_diagram.png")
    #drawer.save_graph(graph, "circuit_graph.png")


def _parse_debug_options():
    parser = argparse.ArgumentParser(description="Quantum circuit simplifier")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    set_debug_mode(args.debug)


if __name__ == "__main__":
    _parse_debug_options()
    _main()
