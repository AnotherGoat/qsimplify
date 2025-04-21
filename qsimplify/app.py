import os

from flask import Flask, jsonify, Response
from dotenv import load_dotenv

from qsimplify.controller.circuit_controller import circuit_controller

load_dotenv()
FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
FLASK_RUN_PORT = os.getenv("FLASK_RUN_PORT", 5000)
FLASK_DEBUG = os.getenv("FLASK_DEBUG", True)

app = Flask(__name__)

@app.route("/api")
def _index() -> tuple[Response | None, int]:
    return jsonify({"message": "Welcome to QSimplify API"}), 200

app.register_blueprint(circuit_controller, url_prefix="/api/circuit")

if __name__ == "__main__":
    app.run(host=FLASK_RUN_HOST, port=FLASK_RUN_PORT, debug=FLASK_DEBUG)
