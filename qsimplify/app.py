"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from qsimplify import logging_config
from qsimplify.controller.circuit_controller import circuit_router
from qsimplify.controller.exception_handlers import (
    handle_gates_validation_error,
    handle_request_validation_error,
)
from qsimplify.model.quantum_gate import GatesValidationError

load_dotenv()
_API_HOST = os.getenv("API_HOST", "localhost")
_API_PORT = int(os.getenv("API_PORT", 5001))
_API_RELOAD = bool(os.getenv("API_RELOAD", True))


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logging_config.set_up_logging()
    yield


app = FastAPI(lifespan=_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(circuit_router)

app.add_exception_handler(RequestValidationError, handle_request_validation_error)
app.add_exception_handler(GatesValidationError, handle_gates_validation_error)


def _custom_schema() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="QSimplify API",
        version="0.0.1",
        description="A REST API for quantum circuit simplification",
        contact={
            "name": "Get help with the usage of this API",
            "email": "v.mardones04@ufromail.cl",
        },
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = _custom_schema


if __name__ == "__main__":
    uvicorn.run(
        "qsimplify.app:app",
        host=_API_HOST,
        port=_API_PORT,
        reload=_API_RELOAD,
    )
