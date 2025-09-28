import importlib

import pytest

from qsimplify import env


def test_parse_default_bools(monkey_patch: pytest.MonkeyPatch):
    monkey_patch.setenv("LOG_TO_FILE", "")
    monkey_patch.setenv("API_RELOAD", "")

    importlib.reload(env)

    assert not env.LOG_TO_FILE
    assert env.API_RELOAD


def test_parse_true_bools(monkey_patch: pytest.MonkeyPatch):
    for key in ("LOG_TO_FILE", "API_RELOAD"):
        for value in ("true", "True", "TRUE"):
            monkey_patch.setenv(key, value)
            importlib.reload(env)
            assert getattr(env, key)


def test_parse_false_bools(monkey_patch: pytest.MonkeyPatch):
    for key in ("LOG_TO_FILE", "API_RELOAD"):
        for value in ("false", "False", "FALSE"):
            monkey_patch.setenv(key, value)
            importlib.reload(env)
            assert not getattr(env, key)


def test_parse_unknown_bools(monkey_patch: pytest.MonkeyPatch):
    monkey_patch.setenv("LOG_TO_FILE", "maybe")
    monkey_patch.setenv("API_RELOAD", "possibly")

    importlib.reload(env)

    assert not env.LOG_TO_FILE
    assert env.API_RELOAD


def test_parse_default_int(monkey_patch: pytest.MonkeyPatch):
    monkey_patch.setenv("API_PORT", "")
    importlib.reload(env)

    assert env.API_PORT == 5000


def test_parse_int(monkey_patch: pytest.MonkeyPatch):
    monkey_patch.setenv("API_PORT", "1234")
    importlib.reload(env)

    assert env.API_PORT == 1234


def test_parse_invalid_ints(monkey_patch: pytest.MonkeyPatch):
    for value in ("abc", "1234.5", "???"):
        monkey_patch.setenv("API_PORT", value)
        importlib.reload(env)

        assert env.API_PORT == 5000


def test_parse_default_log_level(monkey_patch: pytest.MonkeyPatch):
    monkey_patch.setenv("LOG_LEVEL", "")
    importlib.reload(env)

    assert env.LOG_LEVEL == "INFO"


def test_parse_known_log_levels(monkey_patch: pytest.MonkeyPatch):
    for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        monkey_patch.setenv("LOG_LEVEL", level)
        importlib.reload(env)
        assert level == env.LOG_LEVEL


def test_parse_unknown_log_levels(monkey_patch: pytest.MonkeyPatch):
    for level in ("UNKNOWN", "???", "!!!"):
        monkey_patch.setenv("LOG_LEVEL", level)
        importlib.reload(env)
        assert env.LOG_LEVEL == "INFO"
