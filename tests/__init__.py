import math


def floats_equal(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-05, abs_tol=1e-08)
