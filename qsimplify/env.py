"""Contains environment variables that are used across the project."""

import os

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def _parse_bool(key: str, default: bool) -> bool:
    input_value = os.getenv(key)

    if input_value is None:
        return default

    lower_value = input_value.lower()

    if lower_value not in ("true", "false"):
        logger.warning(f"Invalid {key} '{input_value}', defaulting to {default}")
        return default

    return lower_value == "true"


def _parse_int(key: str, default: int) -> int:
    input_value = os.getenv(key)

    if input_value is None:
        return default

    try:
        value = int(input_value)
    except ValueError:
        logger.warning(f"Invalid {key} '{input_value}', defaulting to {default}")
        return default

    return value


def _parse_log_level() -> str:
    input_level = os.getenv("LOG_LEVEL")

    if input_level is None:
        return "INFO"

    level = input_level.upper()

    if level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        logger.warning(f"Unknown LOG_LEVEL '{input_level}', defaulting to INFO")
        return "INFO"

    return level


API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = _parse_int("API_PORT", 5000)
API_RELOAD = _parse_bool("API_RELOAD", True)
LOG_LEVEL = _parse_log_level()
LOG_TO_FILE = _parse_bool("LOG_TO_FILE", False)
