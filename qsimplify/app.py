import os

from flask import Flask, jsonify, Response
from dotenv import load_dotenv

from qsimplify.controller.circuit_controller import circuit_controller

load_dotenv()
app = Flask(__name__)


@app.route("/api")
def _index() -> tuple[Response | None, int]:
    return jsonify({"message": "Welcome to QSimplify API"}), 200

app.register_blueprint(circuit_controller, url_prefix="/api/circuit")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
