"""Contains logging utilities that are used across the project."""

import logging
import sys
from logging import Handler, LogRecord
from typing import TypedDict

from dotenv import load_dotenv
from loguru import logger as loguru_logger
from uvicorn.logging import AccessFormatter, DefaultFormatter

from qsimplify import env

load_dotenv()
_LEVEL_FORMATTER = DefaultFormatter(fmt="%(levelprefix)s")
_UVICORN_FORMATTER = DefaultFormatter(fmt="%(message)s")
_ACCESS_FORMATTER = AccessFormatter(fmt='%(client_addr)s - "%(request_line)s" %(status_code)s')


def _remove_existing_handlers() -> None:
    """Remove all existing handlers from the root logger.

    Prevents duplicate logs from appearing.
    """
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


def _propagate_fastapi_loggers() -> None:
    """Allow FastAPI's internal loggers to reach the root logger, to then be captured by Loguru."""
    loggers = (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "asyncio",
        "starlette",
    )

    for logger_name in loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = []
        logging_logger.propagate = True


class LoguruHandler(Handler):
    """A custom logging interceptor to redirect Python's built-in logging to Loguru.

    This is needed because FastAPI uses Python's built-in logger, which doesn't offer Loguru's ease of use.
    """

    def emit(self, record: LogRecord) -> None:
        """Send a logging record to Loguru."""
        level = self._find_logging_level(record)
        depth = self._find_depth()
        message = self._format_message(record)
        loguru_logger.opt(depth=depth, exception=record.exc_info).log(level, message)

    @staticmethod
    def _find_logging_level(record: LogRecord) -> str | int:
        try:
            return loguru_logger.level(record.levelname).name
        except ValueError:
            return record.levelno

    @staticmethod
    def _find_depth() -> int:
        frame = logging.currentframe()
        depth = 2

        while frame.f_back and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        return depth

    @staticmethod
    def _format_message(record: LogRecord) -> str:
        name = record.name

        if name == "uvicorn":
            return _UVICORN_FORMATTER.format(record)

        if name == "uvicorn.access":
            return _ACCESS_FORMATTER.format(record)

        return record.getMessage()


class _RecordLevel:
    """Defines the used parts of a Loguru log record level.

    This is added here to avoid getting an ImportError: cannot import name 'RecordLevel' from 'loguru'.
    """

    no: int


class _LoguruRecord(TypedDict):
    """Defines the used parts of a Loguru log record.

    This is added here to avoid getting an ImportError: cannot import name 'Record' from 'loguru'.
    """

    level: _RecordLevel
    message: str


def _format_log(record: _LoguruRecord) -> str:
    level = record["level"].no

    log_record = LogRecord(
        name="", level=level, pathname="", lineno=0, msg="", args=(), exc_info=None
    )

    message = record["message"]
    return f"{_LEVEL_FORMATTER.format(log_record)} {message}\n"


def set_up_logging() -> None:
    """Configure the root logger to use Loguru and redirect Python's built-in logger to Loguru's."""
    _remove_existing_handlers()
    _propagate_fastapi_loggers()
    logging.basicConfig(handlers=[LoguruHandler()])
    loguru_logger.remove()

    loguru_logger.add(sys.stdout, format=_format_log, colorize=True, level=env.LOG_LEVEL)

    if env.LOG_TO_FILE:
        loguru_logger.add(
            "logs/app.log",
            rotation="100 MB",
            compression="zip",
            level=logging.DEBUG,
            backtrace=True,
            diagnose=True,
        )
