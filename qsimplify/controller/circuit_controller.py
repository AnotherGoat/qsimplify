from dataclasses import asdict
from typing import Any

from flask import Blueprint, Response, jsonify, request, send_file

from qsimplify.analyzer import analyzer
from qsimplify.analyzer.metrics import DeltaMetrics
from qsimplify.converter import GatesConverter, QiskitConverter
from qsimplify.drawer import Drawer
from qsimplify.generator import QiskitGenerator
from qsimplify.model import quantum_gate
from qsimplify.model.quantum_graph import QuantumGraph
from qsimplify.simplifier import Simplifier

circuit_controller = Blueprint("circuit", __name__)
gates_converter = GatesConverter()
qiskit_converter = QiskitConverter()
simplifier = Simplifier()
drawer = Drawer()
qiskit_generator = QiskitGenerator()


@circuit_controller.post("/simplify")
def _simplify_circuit() -> tuple[Response, int]:
    graph = _json_to_graph(request.get_json()["gates"])
    simplified_graph = simplifier.simplify_graph(graph)
    simplified_gates = [gate.model_dump() for gate in gates_converter.from_graph(simplified_graph)]
    original_metrics = analyzer.calculate_metrics(graph)
    new_metrics = analyzer.calculate_metrics(simplified_graph)
    delta_metrics = analyzer.compare_metrics(graph, simplified_graph)
    build_steps = qiskit_generator.generate(graph)

    result = {
        "gates": simplified_gates,
        "original_metrics": original_metrics,
        "new_metrics": new_metrics,
        "delta_metrics": _remove_empty_metrics(delta_metrics),
        "code": build_steps,
    }

    return jsonify(result), 200


def _json_to_graph(json: Any) -> QuantumGraph:
    gates = quantum_gate.parse_gates(json)
    return gates_converter.to_graph(gates)


def _remove_empty_metrics(metrics: DeltaMetrics) -> dict[str, int]:
    return {
        metric_name: value for metric_name, value in asdict(metrics).items() if value is not None
    }


@circuit_controller.post("/plot")
def _plot_circuit() -> tuple[Response, int]:
    graph = _json_to_graph(request.get_json()["gates"])
    qiskit_circuit = qiskit_converter.from_graph(graph)
    buffer = drawer.save_circuit_to_buffer(qiskit_circuit)
    return send_file(buffer, mimetype="image/png"), 200


@circuit_controller.post("/plot_graph")
def _plot_graph() -> tuple[Response, int]:
    graph = _json_to_graph(request.get_json()["gates"])
    buffer = drawer.save_graph_to_buffer(graph, "png", dpi=str(100))
    return send_file(buffer, mimetype="image/png"), 200


@circuit_controller.post("/code")
def _code_graph() -> tuple[Response, int]:
    graph = _json_to_graph(request.get_json()["gates"])
    build_steps = qiskit_generator.generate(graph)
    return jsonify({"code": build_steps}), 200


@circuit_controller.post("/metrics")
def _calculate_metrics() -> tuple[Response, int]:
    graph = _json_to_graph(request.get_json()["gates"])
    metrics = analyzer.calculate_metrics(graph)
    return jsonify({"metrics": metrics}), 200


@circuit_controller.post("/compare")
def _compare_metrics() -> tuple[Response, int]:
    old = _json_to_graph(request.get_json()["old_gates"])
    new = _json_to_graph(request.get_json()["new_gates"])
    delta_metrics = analyzer.compare_metrics(old, new)
    return jsonify({"delta_metrics": _remove_empty_metrics(delta_metrics)}), 200
