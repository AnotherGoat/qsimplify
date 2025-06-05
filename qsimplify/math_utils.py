import math

import numpy


def are_floats_similar(first: float, second: float) -> bool:
    """Check whether two real numbers are close enough to be considered equal.

    The default tolerance values are the same as the ones from numpy's isclose.
    """
    return math.isclose(first, second, rel_tol=1e-05, abs_tol=1e-08)


def normalize_angle(angle: float, full_cycle: float = 2 * numpy.pi) -> float:
    """Normalize an angle to the range [0, full_cycle)."""
    if not math.isfinite(angle):
        raise ValueError("The angle must be a finite number (not Inf or NaN)")

    return angle % full_cycle
