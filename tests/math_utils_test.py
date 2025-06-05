import math

import numpy
from pytest import raises

from qsimplify import math_utils
from tests import *


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
    with raises(ValueError, match=r"The angle must be a finite number \(not Inf or NaN\)"):
        assert math_utils.normalize_angle(math.inf, 4 * numpy.pi)

    with raises(ValueError, match=r"The angle must be a finite number \(not Inf or NaN\)"):
        assert math_utils.normalize_angle(-math.inf, 4 * numpy.pi)

    with raises(ValueError, match=r"The angle must be a finite number \(not Inf or NaN\)"):
        assert math_utils.normalize_angle(math.nan, 4 * numpy.pi)

    with raises(ValueError, match=r"The angle must be a finite number \(not Inf or NaN\)"):
        assert math_utils.normalize_angle(-math.nan, 4 * numpy.pi)
