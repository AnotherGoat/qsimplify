import os
import signal
import sys

BENCHMARK_JSON_PATH: str | None = None
_BENCHMARK_SESSION = None

# Fix sys.path so qsimplify is importable
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def pytest_sessionstart(session):
    global BENCHMARK_JSON_PATH, _BENCHMARK_SESSION
    bs = session.config._benchmarksession
    _BENCHMARK_SESSION = bs
    if bs and bs.json:
        BENCHMARK_JSON_PATH = bs.json.name


def _save_benchmarks():
    if not BENCHMARK_JSON_PATH:
        return
    bs = _BENCHMARK_SESSION
    if not bs or not bs.benchmarks:
        return
    try:
        from pytest_benchmark.utils import safe_dumps

        machine_info = bs.get_machine_info()
        benchmarks = list(bs.benchmarks)
        output_json = {
            "machine_info": machine_info,
            "commit_info": {},
            "benchmarks": [b.as_dict(include_data=True) for b in benchmarks if not b.has_error],
        }
        with open(BENCHMARK_JSON_PATH, "wb") as f:
            f.write(safe_dumps(output_json, ensure_ascii=True, indent=4).encode())
    except Exception:
        pass


def pytest_runtest_makereport(item, call):
    if call.when == "teardown":
        _save_benchmarks()


_original_sigterm = None


def _sigterm_handler(signum, frame):
    _save_benchmarks()
    if _original_sigterm:
        _original_sigterm(signum, frame)


def pytest_load_initial_conftests(early_config, parser, args):
    global _original_sigterm
    _original_sigterm = signal.signal(signal.SIGTERM, _sigterm_handler)
