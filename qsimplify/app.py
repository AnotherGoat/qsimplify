import os
from flask_cors import  CORS
from dotenv import load_dotenv
from flask import Flask, Response, jsonify

from qsimplify.controller.circuit_controller import circuit_controller

load_dotenv()
_FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
_FLASK_RUN_PORT = os.getenv("FLASK_RUN_PORT", 5001)
_FLASK_DEBUG = os.getenv("FLASK_DEBUG", True)

app = Flask(__name__)
CORS(app)

@app.route("/api")
def _index() -> tuple[Response | None, int]:
    return jsonify({"message": "Welcome to QSimplify API"}), 200


app.register_blueprint(circuit_controller, url_prefix="/api/circuit")

if __name__ == "__main__":
    app.run(host=_FLASK_RUN_HOST, port=_FLASK_RUN_PORT, debug=_FLASK_DEBUG)
