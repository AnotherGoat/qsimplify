import argparse

from qiskit import QuantumCircuit

from qsimplify.analyzer import analyze
from qsimplify.drawer import Drawer
from qsimplify.simplifier import Simplifier
from qsimplify.utils import set_debug_mode
from qsimplify.converter import Converter


def _main():
    circuit = QuantumCircuit(1)

    circuit.h(0)
    circuit.h(0)
    circuit.h(0)

    converter = Converter()
    graph = converter.circuit_to_graph(circuit)

    print(graph)

    simplifier = Simplifier(converter)
    simplified_circuit = converter.graph_to_circuit(simplifier.simplify_graph(graph))

    print(circuit.draw())
    print(simplified_circuit.draw())


def _demo():
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.id(0)
    circuit.h(0)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.h(0)
    circuit.id(0)
    circuit.h(0)
    circuit.id(0)
    circuit.h(0)

    print("\n===== Original circuit =====")
    print(circuit.draw())

    converter = Converter()

    graph = converter.circuit_to_graph(circuit)
    print("\n===== Original grid =====")
    print(graph.draw_grid())

    print("\n===== Original graph =====")
    print(graph)

    metrics = analyze(circuit, converter)
    print("\n===== Original metrics =====")
    print(metrics)

    simplifier = Simplifier(converter)

    simplified_circuit, build_steps = converter.graph_to_circuit(simplifier.simplify_graph(graph))
    print("\n===== Simplified circuit =====")
    print(simplified_circuit.draw())

    print("\n===== Simplified build steps =====")
    print("\n".join(build_steps))

    simplified_metrics = analyze(simplified_circuit, converter)
    print("\n===== Simplified metrics =====")
    print(simplified_metrics)

    drawer = Drawer()
    #drawer.save_circuit(circuit, "original_circuit.png")
    #drawer.save_graph(graph, "original_graph.png", draw_legend=False)
    #drawer.save_circuit(simplified_circuit, "simplified_circuit.png")
    #drawer.save_graph(converter.circuit_to_graph(simplified_circuit), "simplified_graph.png", draw_legend=False)


def _parse_debug_options():
    parser = argparse.ArgumentParser(description="Quantum circuit simplifier")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    set_debug_mode(args.debug)


if __name__ == "__main__":
    _parse_debug_options()
    _demo()