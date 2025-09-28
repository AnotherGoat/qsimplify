"""Quantum circuit simplification demo, which showcases."""

from pathlib import Path

from loguru import logger
from qiskit import QuantumCircuit

from qsimplify import drawer, logging_config
from qsimplify.analyzer import analyzer
from qsimplify.converter import QiskitConverter
from qsimplify.generator.qiskit_generator import QiskitGenerator
from qsimplify.simplifier import Simplifier

logging_config.set_up_logging()


def _run_demo() -> None:
    circuit = QuantumCircuit(3)
    circuit.cx(0, 1)
    circuit.id(1)
    circuit.x(0)
    circuit.id(0)
    circuit.cx(0, 1)

    logger.info(f"===== Original circuit =====\n{circuit.draw()}")

    qiskit_converter = QiskitConverter()
    graph = qiskit_converter.to_graph(circuit)

    logger.info(f"===== Original grid =====\n{graph.draw_grid()}")
    logger.info(f"===== Original graph =====\n{graph}")

    metrics = analyzer.calculate_detailed_metrics(graph)

    logger.info(f"===== Original metrics =====\n{metrics}")

    simplifier = Simplifier()
    simplified_graph = simplifier.simplify_graph(graph)
    simplified_circuit = qiskit_converter.from_graph(simplified_graph)

    logger.info(f"===== Simplified circuit =====\n{simplified_circuit.draw()}")

    qiskit_generator = QiskitGenerator()
    build_steps = qiskit_generator.generate(simplified_graph)

    logger.info(f"===== Simplified build steps =====\n{build_steps}")

    simplified_metrics = analyzer.calculate_detailed_metrics(simplified_graph)
    logger.info(f"===== Simplified metrics ====={simplified_metrics}")

    Path("out").mkdir(exist_ok=True)

    drawer.save_circuit_png(circuit, "out/original_circuit")
    drawer.save_graph_png(graph, "out/original_graph")
    drawer.save_graph_svg(graph, "out/original_graph")
    drawer.save_circuit_png(simplified_circuit, "out/simplified_circuit")
    drawer.save_graph_png(simplified_graph, "out/simplified_graph")
    drawer.save_graph_svg(simplified_graph, "out/simplified_graph")


if __name__ == "__main__":
    _run_demo()
