"""Contains global exception handlers for the REST API."""

from http import HTTPStatus

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from qsimplify.controller.dto import ErrorList, GateListErrors
from qsimplify.model.quantum_gate import GatesValidationError


def _format_error_message(error: dict) -> str:
    message = error.get("msg", "Unknown error")

    if message.startswith("Value error, "):
        message = message.replace("Value error, ", "", 1)

    location = error.get("loc", ["???"])

    if location[0] == "body":
        location = location[1:]

    formatted_location = ".".join(str(location_name) for location_name in location)
    return f"{formatted_location}: {message}"


def _extract_error_messages(validation_error: RequestValidationError) -> list[str]:
    return [_format_error_message(error) for error in validation_error.errors()]


async def handle_request_validation_error(
    _: Request, exception: RequestValidationError
) -> JSONResponse:
    """Intercept a RequestValidationError with a more helpful response."""
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(ErrorList(errors=_extract_error_messages(exception))),
    )


async def handle_gates_validation_error(
    _: Request, exception: GatesValidationError
) -> JSONResponse:
    """Intercept a GatesValidationError to send a response containing errors for each wrong gate."""
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(GateListErrors(errors=exception.errors)),
    )
