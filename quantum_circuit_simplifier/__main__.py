import argparse

from qiskit import QuantumCircuit

from quantum_circuit_simplifier.analyzer import analyze
from quantum_circuit_simplifier.drawer import Drawer
from quantum_circuit_simplifier.utils import set_debug_mode
from quantum_circuit_simplifier.converter import Converter


def _main():
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.cx(0, 1)

    print("\n===== Circuit drawing =====")
    print(circuit.draw())

    converter = Converter()

    grid = converter.circuit_to_grid(circuit)
    print("\n===== Circuit grid =====")
    print(grid)

    graph = converter.grid_to_graph(grid)
    print("\n===== Circuit graph =====")
    print(graph)

    metrics = analyze(circuit, converter)
    print("\n===== Circuit metrics =====")
    print(metrics)

    converted_circuit = converter.graph_to_circuit(graph)
    print("\n===== Converted circuit =====")
    print(converted_circuit.draw())

    drawer = Drawer()
    drawer.save_circuit(circuit, "circuit_diagram.png")
    drawer.save_graph(graph, "circuit_graph.png", draw_legend=False)


def _parse_debug_options():
    parser = argparse.ArgumentParser(description="Quantum circuit simplifier")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    set_debug_mode(args.debug)


if __name__ == "__main__":
    _parse_debug_options()
    _main()
