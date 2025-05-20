import pytest
from flask import Flask

from qsimplify.controller.circuit_controller import circuit_controller


@pytest.fixture
def _client():
    app = Flask(__name__)
    app.register_blueprint(circuit_controller, url_prefix="/api/circuit")
    app.testing = True
    with app.test_client() as client:
        yield client
