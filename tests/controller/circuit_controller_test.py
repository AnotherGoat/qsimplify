import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from qsimplify.controller.circuit_controller import circuit_router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(circuit_router, prefix="/api/circuit")

    with TestClient(app) as client:
        yield client
