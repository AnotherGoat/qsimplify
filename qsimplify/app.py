"""FastAPI application entry point."""

import os
from dataclasses import dataclass
from http import HTTPStatus

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from qsimplify.controller.circuit_controller import circuit_router
from qsimplify.controller.index_controller import index_router
from qsimplify.model.quantum_gate import GatesValidationError

load_dotenv()
_API_HOST = os.getenv("API_HOST", "localhost")
_API_PORT = int(os.getenv("API_PORT", 5001))
_API_DEBUG = bool(os.getenv("API_DEBUG", True))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(index_router)
app.include_router(circuit_router)


@dataclass(frozen=True)
class GateListErrors:
    """Error messages for a failed validation of a list of gates."""

    errors: dict[int, list[str]]


@app.exception_handler(GatesValidationError)
async def _handle_gates_validation_error(
    _: Request, exception: GatesValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content=jsonable_encoder(GateListErrors(exception.errors)),
    )


if __name__ == "__main__":
    uvicorn.run("qsimplify.app:app", host=_API_HOST, port=_API_PORT, reload=_API_DEBUG)
