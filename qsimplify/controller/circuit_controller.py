from typing import Any

from flask import Blueprint, Response, jsonify, request, send_file

from qsimplify.analyzer import analyzer
from qsimplify.converter import GatesConverter, QiskitConverter
from qsimplify.drawer import Drawer
from qsimplify.generator.qiskit_generator import QiskitGenerator
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
    return jsonify(simplified_gates), 200


def _json_to_graph(json: Any) -> QuantumGraph:
    gates = quantum_gate.parse_gates(json)
    return gates_converter.to_graph(gates)


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
def _calculate_detailed_metrics() -> tuple[Response, int]:
    graph = _json_to_graph(request.get_json()["gates"])
    metrics = analyzer.calculate_metrics(graph)
    return jsonify({"metrics": metrics}), 200
