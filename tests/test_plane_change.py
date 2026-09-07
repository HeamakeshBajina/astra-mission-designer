"""Tests for orbital plane-change calculations."""

import math

import pytest

from astra.physics.constants import EARTH_MU
from astra.physics.plane_change import plane_change_delta_v


def test_zero_plane_change_requires_zero_delta_v():
    delta_v = plane_change_delta_v(
        radius=7_000_000,
        inclination_change=0,
    )

    assert delta_v == pytest.approx(0.0)


def test_plane_change_matches_analytical_equation():
    radius = 7_000_000
    inclination_change = 30

    orbital_velocity = math.sqrt(EARTH_MU / radius)

    expected = (
        2
        * orbital_velocity
        * math.sin(math.radians(inclination_change) / 2)
    )

    actual = plane_change_delta_v(
        radius,
        inclination_change,
    )

    assert actual == pytest.approx(expected)


def test_larger_plane_change_requires_more_delta_v():
    radius = 7_000_000

    delta_v_10 = plane_change_delta_v(
        radius,
        10,
    )

    delta_v_30 = plane_change_delta_v(
        radius,
        30,
    )

    delta_v_60 = plane_change_delta_v(
        radius,
        60,
    )

    assert delta_v_10 < delta_v_30 < delta_v_60


def test_invalid_radius_is_rejected():
    with pytest.raises(ValueError):
        plane_change_delta_v(
            radius=0,
            inclination_change=10,
        )


def test_negative_inclination_change_is_rejected():
    with pytest.raises(ValueError):
        plane_change_delta_v(
            radius=7_000_000,
            inclination_change=-10,
        )


def test_inclination_change_above_180_degrees_is_rejected():
    with pytest.raises(ValueError):
        plane_change_delta_v(
            radius=7_000_000,
            inclination_change=181,
        )