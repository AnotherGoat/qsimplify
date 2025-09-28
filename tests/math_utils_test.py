import math
from fractions import Fraction

import numpy
import pytest

from qsimplify import math_utils

ANGLE_FINITE = r"The angle must be a finite number \(not Inf or NaN\)"


def test_are_different_floats_similar():
    assert not math_utils.are_floats_similar(5, 10)
    assert not math_utils.are_floats_similar(-3, 3)


def test_are_close_floats_similar():
    assert not math_utils.are_floats_similar(0, 1)
    assert not math_utils.are_floats_similar(0, 0.1)
    assert not math_utils.are_floats_similar(0, 0.01)
    assert not math_utils.are_floats_similar(0, 0.001)
    assert not math_utils.are_floats_similar(0, 0.0001)
    assert not math_utils.are_floats_similar(0, 0.00001)
    assert not math_utils.are_floats_similar(0, 0.000001)
    assert not math_utils.are_floats_similar(0, 0.0000001)


def test_are_very_close_floats_similar():
    assert math_utils.are_floats_similar(0, 0.00000001)
    assert math_utils.are_floats_similar(0.3, 0.30000001)
    assert math_utils.are_floats_similar(3.14159, numpy.pi)


def test_normalize_zero_angle():
    assert math_utils.are_floats_similar(math_utils.normalize_angle(0, 4 * numpy.pi), 0)
    assert math_utils.are_floats_similar(math_utils.normalize_angle(-0, 4 * numpy.pi), 0)


def test_normalize_positive_angle():
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(numpy.pi, 4 * numpy.pi), numpy.pi
    )
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(2 * numpy.pi, 4 * numpy.pi), 2 * numpy.pi
    )
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(3 * numpy.pi, 4 * numpy.pi), 3 * numpy.pi
    )
    assert math_utils.are_floats_similar(math_utils.normalize_angle(4 * numpy.pi, 4 * numpy.pi), 0)
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(5 * numpy.pi, 4 * numpy.pi), numpy.pi
    )
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(6 * numpy.pi, 4 * numpy.pi), 2 * numpy.pi
    )
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(7 * numpy.pi, 4 * numpy.pi), 3 * numpy.pi
    )
    assert math_utils.are_floats_similar(math_utils.normalize_angle(8 * numpy.pi, 4 * numpy.pi), 0)


def test_normalize_negative_angle():
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(-numpy.pi, 4 * numpy.pi), 3 * numpy.pi
    )
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(-2 * numpy.pi, 4 * numpy.pi), 2 * numpy.pi
    )
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(-3 * numpy.pi, 4 * numpy.pi), numpy.pi
    )
    assert math_utils.are_floats_similar(math_utils.normalize_angle(-4 * numpy.pi, 4 * numpy.pi), 0)
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(-5 * numpy.pi, 4 * numpy.pi), 3 * numpy.pi
    )
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(-6 * numpy.pi, 4 * numpy.pi), 2 * numpy.pi
    )
    assert math_utils.are_floats_similar(
        math_utils.normalize_angle(-7 * numpy.pi, 4 * numpy.pi), numpy.pi
    )
    assert math_utils.are_floats_similar(math_utils.normalize_angle(-8 * numpy.pi, 4 * numpy.pi), 0)


def test_normalize_edge_case_angles():
    with pytest.raises(ValueError, match=ANGLE_FINITE):
        math_utils.normalize_angle(math.inf, 4 * numpy.pi)

    with pytest.raises(ValueError, match=ANGLE_FINITE):
        math_utils.normalize_angle(-math.inf, 4 * numpy.pi)

    with pytest.raises(ValueError, match=ANGLE_FINITE):
        math_utils.normalize_angle(math.nan, 4 * numpy.pi)

    with pytest.raises(ValueError, match=ANGLE_FINITE):
        math_utils.normalize_angle(-math.nan, 4 * numpy.pi)


def test_rationalize_zero_in_terms_of_pi():
    assert math_utils.rationalize_in_terms_of_pi(0) == Fraction(0, 1)


def test_rationalize_positive_multiples_of_pi():
    assert math_utils.rationalize_in_terms_of_pi(numpy.pi) == Fraction(1, 1)
    assert math_utils.rationalize_in_terms_of_pi(2 * numpy.pi) == Fraction(2, 1)
    assert math_utils.rationalize_in_terms_of_pi(3 * numpy.pi) == Fraction(3, 1)


def test_rationalize_negative_multiples_of_pi():
    assert math_utils.rationalize_in_terms_of_pi(-numpy.pi) == Fraction(-1, 1)
    assert math_utils.rationalize_in_terms_of_pi(-2 * numpy.pi) == Fraction(-2, 1)
    assert math_utils.rationalize_in_terms_of_pi(-3 * numpy.pi) == Fraction(-3, 1)


def test_rationalize_non_multiples_of_pi():
    assert math_utils.rationalize_in_terms_of_pi(-2.5) is None
    assert math_utils.rationalize_in_terms_of_pi(-1.4) is None
    assert math_utils.rationalize_in_terms_of_pi(-0.3) is None
    assert math_utils.rationalize_in_terms_of_pi(0.3) is None
    assert math_utils.rationalize_in_terms_of_pi(1.4) is None
    assert math_utils.rationalize_in_terms_of_pi(2.5) is None


def test_rationalize_fractions_of_pi():
    assert math_utils.rationalize_in_terms_of_pi(-1 * numpy.pi / 2) == Fraction(-1, 2)
    assert math_utils.rationalize_in_terms_of_pi(2 * numpy.pi / 3) == Fraction(2, 3)
    assert math_utils.rationalize_in_terms_of_pi(-3 * numpy.pi / 4) == Fraction(-3, 4)
    assert math_utils.rationalize_in_terms_of_pi(5 * numpy.pi / 6) == Fraction(5, 6)
    assert math_utils.rationalize_in_terms_of_pi(-7 * numpy.pi / 8) == Fraction(-7, 8)
    assert math_utils.rationalize_in_terms_of_pi(11 * numpy.pi / 12) == Fraction(11, 12)
    assert math_utils.rationalize_in_terms_of_pi(-15 * numpy.pi / 16) == Fraction(-15, 16)


def test_rationalize_big_pi_denominators():
    assert math_utils.rationalize_in_terms_of_pi(numpy.pi / 17) is None
    assert math_utils.rationalize_in_terms_of_pi(numpy.pi / 18) is None
    assert math_utils.rationalize_in_terms_of_pi(numpy.pi / 19) is None
    assert math_utils.rationalize_in_terms_of_pi(numpy.pi / 100) is None
    assert math_utils.rationalize_in_terms_of_pi(numpy.pi / 1000) is None


def test_format_zero_angle():
    assert math_utils.format_angle(0) == "0"
    assert math_utils.format_angle(-0) == "0"
    assert math_utils.format_angle(0.00000001) == "0"
    assert math_utils.format_angle(-0.00000001) == "0"


def test_format_pi_angles_without_denominator():
    assert math_utils.format_angle(-3 * numpy.pi) == "-3π"
    assert math_utils.format_angle(-2 * numpy.pi) == "-2π"
    assert math_utils.format_angle(-numpy.pi) == "-π"
    assert math_utils.format_angle(numpy.pi) == "π"
    assert math_utils.format_angle(2 * numpy.pi) == "2π"
    assert math_utils.format_angle(3 * numpy.pi) == "3π"


def test_format_pi_angles_without_numerator():
    assert math_utils.format_angle(numpy.pi / 2) == "π/2"
    assert math_utils.format_angle(-numpy.pi / 2) == "-π/2"
    assert math_utils.format_angle(numpy.pi / 3) == "π/3"
    assert math_utils.format_angle(-numpy.pi / 3) == "-π/3"
    assert math_utils.format_angle(numpy.pi / 4) == "π/4"
    assert math_utils.format_angle(-numpy.pi / 4) == "-π/4"


def test_format_pi_full_fraction_angles():
    assert math_utils.format_angle(2 * numpy.pi / 3) == "2π/3"
    assert math_utils.format_angle(-2 * numpy.pi / 3) == "-2π/3"
    assert math_utils.format_angle(7 * numpy.pi / 10) == "7π/10"
    assert math_utils.format_angle(-7 * numpy.pi / 10) == "-7π/10"


def test_format_non_pi_angles():
    assert math_utils.format_angle(2.55) == "2.55"
    assert math_utils.format_angle(-1.44) == "-1.44"
    assert math_utils.format_angle(-0.33) == "-0.33"
    assert math_utils.format_angle(0.33) == "0.33"
    assert math_utils.format_angle(1.44) == "1.44"
    assert math_utils.format_angle(2.55) == "2.55"


def test_format_angles_with_trailing_zeroes():
    assert math_utils.format_angle(3) == "3"
    assert math_utils.format_angle(-3) == "-3"
    assert math_utils.format_angle(1.5) == "1.5"
    assert math_utils.format_angle(-1.5) == "-1.5"
