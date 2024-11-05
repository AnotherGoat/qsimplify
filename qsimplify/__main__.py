import argparse

from qiskit import QuantumCircuit

from qsimplify.analyzer import Analyzer
from qsimplify.drawer import Drawer
from qsimplify.simplifier import Simplifier
from qsimplify.utils import set_debug_mode
from qsimplify.converter import Converter

def _main():
    circuit = QuantumCircuit(5)
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
    simplifier = Simplifier(converter)
    #simplified_circuit, build_steps = simplifier.simplify_circuit(circuit, add_build_steps=True)

    #print("\n===== Simplified circuit =====")
    #print(simplified_circuit.draw())

    #print("\n===== Simplified build steps =====")
    #print(build_steps)

    #drawer = Drawer()
    #drawer.save_circuit_png(circuit, "original_circuit")
    #drawer.save_graph_png(converter.circuit_to_graph(circuit), "original_graph")
    #drawer.save_graph_svg(converter.circuit_to_graph(circuit), "original_graph")
    #drawer.save_circuit(simplified_circuit, "simplified_circuit.png")
    #drawer.save_graph(converter.circuit_to_graph(simplified_circuit), "simplified_graph.png", draw_legend=False)

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

    analyzer = Analyzer(converter)

    metrics = analyzer.calculate_metrics(circuit)
    print("\n===== Original metrics =====")
    print(metrics)

    simplifier = Simplifier(converter)

    simplified_graph = simplifier.simplify_graph(graph)
    simplified_circuit, build_steps = converter.graph_to_circuit(simplified_graph, add_build_steps=True)
    print("\n===== Simplified circuit =====")
    print(simplified_circuit.draw())

    print("\n===== Simplified build steps =====")
    print("\n".join(build_steps))

    simplified_metrics = analyzer.calculate_metrics(simplified_circuit)
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
    _main()
