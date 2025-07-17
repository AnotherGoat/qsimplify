"""A controller for the /api endpoint."""

from http import HTTPStatus

from fastapi import APIRouter

from qsimplify.controller.dto import MessageResponse

index_router = APIRouter(prefix="/api")


@index_router.get("", status_code=HTTPStatus.OK)
def _index() -> MessageResponse:
    return MessageResponse("Welcome to QSimplify API")
