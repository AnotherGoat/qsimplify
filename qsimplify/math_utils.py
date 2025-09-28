"""Contains utility functions related to general use math."""

import math
from fractions import Fraction

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


def rationalize_in_terms_of_pi(number: float) -> Fraction | None:
    """Rationalize a number as a multiple of pi. For example, 1.5 * pi becomes 3 * pi / 2.

    Returns None if the number is not close to being a multiple of pi.
    """
    pi_factor = number / numpy.pi
    fraction = Fraction(pi_factor).limit_denominator(16)

    if numpy.isclose(fraction.numerator / fraction.denominator, pi_factor):
        return fraction

    return None


def _trim_trailing_zeroes(angle: str) -> str:
    return angle.rstrip("0").rstrip(".")


def format_angle(angle: float) -> str:
    """Returns a nicely formatted string for the provided angle, where multiples of pi are used wheneveer possible."""
    if numpy.isclose(angle, 0):
        return "0"

    result = rationalize_in_terms_of_pi(angle)

    if result is None:
        return _trim_trailing_zeroes(f"{angle:.2f}")

    numerator, denominator = result.numerator, result.denominator

    if numerator == denominator:
        return "π"

    if numerator == -denominator:
        return "-π"

    if numerator == 1:
        return f"π/{denominator}"

    if numerator == -1:
        return f"-π/{denominator}"

    if denominator == 1:
        return f"{numerator}π"

    return f"{numerator}π/{denominator}"
