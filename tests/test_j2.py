"""Tests for ASTRA's Earth J2 perturbation model."""

import math

import pytest

from astra.physics.j2 import (
    EARTH_J2,
    j2_acceleration,
)


def test_j2_constant_is_positive():
    """Earth's J2 coefficient should be positive."""

    assert EARTH_J2 > 0


def test_j2_rejects_center_of_earth():
    """J2 acceleration is undefined at Earth's center."""

    with pytest.raises(ValueError):
        j2_acceleration(
            0.0,
            0.0,
            0.0,
        )


def test_j2_has_no_y_component_on_x_axis():
    """A spacecraft on the x-axis should have no J2 y acceleration."""

    ax, ay, az = j2_acceleration(
        7_000_000.0,
        0.0,
        0.0,
    )

    assert ax != 0.0
    assert ay == pytest.approx(0.0)
    assert az == pytest.approx(0.0)


def test_j2_has_expected_symmetry():
    """Changing x sign should change ax sign but preserve magnitude."""

    positive = j2_acceleration(
        7_000_000.0,
        0.0,
        0.0,
    )

    negative = j2_acceleration(
        -7_000_000.0,
        0.0,
        0.0,
    )

    assert negative[0] == pytest.approx(
        -positive[0]
    )

    assert negative[1] == pytest.approx(
        positive[1]
    )

    assert negative[2] == pytest.approx(
        positive[2]
    )


def test_j2_magnitude_decreases_with_altitude():
    """J2 acceleration should become weaker farther from Earth."""

    low = j2_acceleration(
        7_000_000.0,
        0.0,
        0.0,
    )

    high = j2_acceleration(
        14_000_000.0,
        0.0,
        0.0,
    )

    low_magnitude = math.sqrt(
        sum(component**2 for component in low)
    )

    high_magnitude = math.sqrt(
        sum(component**2 for component in high)
    )

    assert high_magnitude < low_magnitude


def test_j2_is_much_smaller_than_central_gravity():
    """J2 should be a perturbation, much smaller than central gravity."""

    radius = 7_000_000.0

    j2 = j2_acceleration(
        radius,
        0.0,
        0.0,
    )

    j2_magnitude = math.sqrt(
        sum(component**2 for component in j2)
    )

    central_gravity = 3.986004418e14 / radius**2

    assert j2_magnitude < central_gravity
    assert j2_magnitude / central_gravity < 0.01