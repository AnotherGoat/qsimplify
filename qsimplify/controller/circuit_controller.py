from typing import Any

from flask import Blueprint, request, jsonify, Response
from pydantic import ValidationError
from pydantic_core import ErrorDetails

from qsimplify.converter import DtoConverter
from qsimplify.dto import quantum_gate
from qsimplify.simplifier import Simplifier

type Errors = dict[int, list[str]]

circuit_controller = Blueprint("circuit", __name__)
dto_converter = DtoConverter()
simplifier = Simplifier()


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
