import os
from typing import Any

from flask import Flask, jsonify, request, Response
from dotenv import load_dotenv

from qsimplify.controller import validator

load_dotenv()
app = Flask(__name__)


@app.route("/")
def index() -> Response:
    data = []
    return jsonify([gate.dict() for gate in data])


@app.post("/circuit/check")
def check_circuit() -> tuple[Response | None, int]:
    gates_data = request.get_json()

    if not isinstance(gates_data, list):
        return jsonify({"errors": {"non_field": ["Expected a list of gates"]}}), 400

    validation_errors = validator.validate_gates(gates_data)

    if validation_errors:
        return jsonify({"errors": validation_errors}), 400

    return Response(), 204


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", False))
