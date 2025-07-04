from pathlib import Path

from qiskit import QuantumCircuit

from qsimplify.analyzer import analyzer
from qsimplify.converter import QiskitConverter
from qsimplify.drawer import Drawer
from qsimplify.generator.qiskit_generator import QiskitGenerator
from qsimplify.simplifier import Simplifier


def _run_demo() -> None:
    circuit = QuantumCircuit(3)
    circuit.cx(0, 1)
    circuit.id(1)
    circuit.x(0)
    circuit.id(0)
    circuit.cx(0, 1)

    print("\n===== Original circuit =====")
    print(circuit.draw())

    qiskit_converter = QiskitConverter()
    graph = qiskit_converter.to_graph(circuit)

    print("\n===== Original grid =====")
    print(graph.draw_grid())

    print("\n===== Original graph =====")
    print(graph)

    metrics = analyzer.calculate_detailed_metrics(graph)

    print("\n===== Original metrics =====")
    print(metrics)

    simplifier = Simplifier()
    simplified_graph = simplifier.simplify_graph(graph)
    simplified_circuit = qiskit_converter.from_graph(simplified_graph)

    print("\n===== Simplified circuit =====")
    print(simplified_circuit.draw())

    qiskit_generator = QiskitGenerator()
    build_steps = qiskit_generator.generate(simplified_graph)

    print("\n===== Simplified build steps =====")
    print(build_steps)

    simplified_metrics = analyzer.calculate_detailed_metrics(simplified_graph)
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


if __name__ == "__main__":
    _run_demo()
