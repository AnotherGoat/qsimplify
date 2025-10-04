import importlib

import pytest

from qsimplify import env


def test_parse_default_bools(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LOG_TO_FILE", "")
    monkeypatch.setenv("API_RELOAD", "")

    importlib.reload(env)

    assert not env.LOG_TO_FILE
    assert env.API_RELOAD


def test_parse_true_bools(monkeypatch: pytest.MonkeyPatch):
    for key in ("LOG_TO_FILE", "API_RELOAD"):
        for value in ("true", "True", "TRUE"):
            monkeypatch.setenv(key, value)
            importlib.reload(env)
            assert getattr(env, key)


def test_parse_false_bools(monkeypatch: pytest.MonkeyPatch):
    for key in ("LOG_TO_FILE", "API_RELOAD"):
        for value in ("false", "False", "FALSE"):
            monkeypatch.setenv(key, value)
            importlib.reload(env)
            assert not getattr(env, key)


def test_parse_unknown_bools(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LOG_TO_FILE", "maybe")
    monkeypatch.setenv("API_RELOAD", "possibly")

    importlib.reload(env)

    assert not env.LOG_TO_FILE
    assert env.API_RELOAD


def test_parse_default_int(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_PORT", "")
    importlib.reload(env)

    assert env.API_PORT == 5000


def test_parse_int(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_PORT", "1234")
    importlib.reload(env)

    assert env.API_PORT == 1234


def test_parse_invalid_ints(monkeypatch: pytest.MonkeyPatch):
    for value in ("abc", "1234.5", "???"):
        monkeypatch.setenv("API_PORT", value)
        importlib.reload(env)

        assert env.API_PORT == 5000


def test_parse_default_log_level(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LOG_LEVEL", "")
    importlib.reload(env)

    assert env.LOG_LEVEL == "INFO"


def test_parse_known_log_levels(monkeypatch: pytest.MonkeyPatch):
    for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        monkeypatch.setenv("LOG_LEVEL", level)
        importlib.reload(env)
        assert level == env.LOG_LEVEL


def test_parse_unknown_log_levels(monkeypatch: pytest.MonkeyPatch):
    for level in ("UNKNOWN", "???", "!!!"):
        monkeypatch.setenv("LOG_LEVEL", level)
        importlib.reload(env)
        assert env.LOG_LEVEL == "INFO"
