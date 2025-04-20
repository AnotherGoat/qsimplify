from io import BytesIO
from typing import Any

from flask import Blueprint, request, jsonify, Response, send_file
from matplotlib import pyplot
from pydantic import ValidationError
from pydantic_core import ErrorDetails

from qsimplify.converter import DtoConverter, QiskitConverter
from qsimplify.drawer import Drawer
from qsimplify.dto import quantum_gate
from qsimplify.simplifier import Simplifier

type Errors = dict[int, list[str]]

circuit_controller = Blueprint("circuit", __name__)
dto_converter = DtoConverter()
qiskit_converter = QiskitConverter()
simplifier = Simplifier()
drawer = Drawer()

@circuit_controller.post("/circuit/simplify")
def _simplify_circuit() -> tuple[Response | None, int]:
    gates_json = request.get_json()
    validation_result = _validate_request(gates_json)

    if validation_result is not None:
        return validation_result

    gates = quantum_gate.parse_gates(gates_json)
    graph = dto_converter.to_graph(gates)
    simplified_graph = simplifier.simplify_graph(graph)
    simplified_gates = [gate.model_dump() for gate in dto_converter.from_graph(simplified_graph)]
    return jsonify(simplified_gates), 200


def _validate_request(gates: Any) -> tuple[Response | None, int] | None:
    if not isinstance(gates, list):
        return jsonify({"errors": {"non_field": ["Expected a list of gates"]}}), 400

    validation_errors = _validate_gates(gates)

    if validation_errors:
        return jsonify({"errors": validation_errors}), 400

    return None


def _validate_gates(gates: list[dict]) -> Errors:
    errors: Errors = {}

    for idx, json in enumerate(gates):
        try:
            quantum_gate.parse_gate(json)
        except ValidationError as error:
            errors[idx] = _extract_error_messages(error)
        except Exception as error:
            errors[idx] = [f"unknown: {error}"]

    return errors


def _extract_error_messages(validation_error: ValidationError) -> list[str]:
    return [_format_error_message(error) for error in validation_error.errors()]


def _format_error_message(error: ErrorDetails) -> str:
    print(error)
    location = error["loc"][-1]
    message = error["msg"]
    return f"{location}: {message}"


@circuit_controller.post("/circuit/plot")
def _plot_circuit() -> tuple[Response | None, int]:
    gates_json = request.get_json()
    validation_result = _validate_request(gates_json)

    if validation_result is not None:
        return validation_result

    gates = quantum_gate.parse_gates(gates_json)
    graph = dto_converter.to_graph(gates)
    qiskit_circuit = qiskit_converter.graph_to_circuit(graph)

    buffer = drawer.save_circuit_to_buffer(qiskit_circuit)
    return send_file(buffer, mimetype="image/png"), 200

@circuit_controller.post("/circuit/plot_graph")
def _plot_graph() -> tuple[Response | None, int]:
    gates_json = request.get_json()
    validation_result = _validate_request(gates_json)

    if validation_result is not None:
        return validation_result

    gates = quantum_gate.parse_gates(gates_json)
    graph = dto_converter.to_graph(gates)

    buffer = drawer.save_graph_to_buffer(graph, "png", dpi=str(100))
    return send_file(buffer, mimetype="image/png"), 200
