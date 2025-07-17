"""Contains general utilities that are used across the project."""

import logging
import os
from logging import Logger

from dotenv import load_dotenv

load_dotenv()
_DEBUG_MODE = os.getenv("DEBUG", False)


def setup_logger(name: str) -> Logger:
    """Create a new logger instance, using the passed name as an identifier."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if _DEBUG_MODE else logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if _DEBUG_MODE else logging.INFO)

    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
