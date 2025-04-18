import argparse
import logging
from logging import Logger


def parse_debug_options() -> bool:
    parser = argparse.ArgumentParser(description="Quantum circuit simplifier")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    return args.debug


_debug_mode = parse_debug_options()


def setup_logger(name: str) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if _debug_mode else logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if _debug_mode else logging.INFO)

    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
