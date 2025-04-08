import argparse
from pathlib import Path

from qiskit import QuantumCircuit

from qsimplify.analyzer import Analyzer
from qsimplify.converter import Converter
from qsimplify.drawer import Drawer
from qsimplify.simplifier import Simplifier
from qsimplify.utils import set_debug_mode


def _main():
    circuit = QuantumCircuit(3)
    circuit.cx(0, 1)
    circuit.id(1)
    circuit.x(0)
    circuit.id(0)
    circuit.cx(0, 1)

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
    simplified_circuit, build_steps = converter.graph_to_circuit(
        simplified_graph, add_build_steps=True
    )

    print("\n===== Simplified circuit =====")
    print(simplified_circuit.draw())

    print("\n===== Simplified build steps =====")
    print(build_steps)

    simplified_metrics = analyzer.calculate_metrics(simplified_circuit)
    print("\n===== Simplified metrics =====")
    print(simplified_metrics)

    Path("out").mkdir(exist_ok=True)

    drawer = Drawer()
    drawer.save_circuit_png(circuit, "out/original_circuit")
    drawer.save_graph_png(graph, "out/original_graph")
    drawer.save_graph_svg(graph, "out/original_graph")
    drawer.save_circuit_png(simplified_circuit, "out/simplified_circuit")
    drawer.save_graph_png(simplified_graph, "out/simplified_graph")
    drawer.save_graph_svg(simplified_graph, "out/simplified_graph")


def _parse_debug_options():
    parser = argparse.ArgumentParser(description="Quantum circuit simplifier")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    set_debug_mode(args.debug)


if __name__ == "__main__":
    _parse_debug_options()
    _main()
