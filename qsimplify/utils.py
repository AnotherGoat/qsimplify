import logging

_debug_mode = False

def set_debug_mode(debug):
    global _debug_mode
    _debug_mode = debug


def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if _debug_mode else logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if _debug_mode else logging.INFO)

    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
