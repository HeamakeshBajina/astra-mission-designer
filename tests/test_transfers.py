import math

import pytest

from astra.physics.constants import EARTH_MU, EARTH_RADIUS
from astra.physics.transfers import hohmann_transfer


def test_transfer_semi_major_axis():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    result = hohmann_transfer(initial_radius, final_radius)

    expected = (initial_radius + final_radius) / 2

    assert math.isclose(
        result.transfer_semi_major_axis,
        expected,
    )


def test_delta_v_is_positive():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    result = hohmann_transfer(initial_radius, final_radius)

    assert result.first_burn_delta_v > 0
    assert result.second_burn_delta_v > 0
    assert result.total_delta_v > 0


def test_total_delta_v_is_sum_of_burns():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    result = hohmann_transfer(initial_radius, final_radius)

    assert math.isclose(
        result.total_delta_v,
        result.first_burn_delta_v + result.second_burn_delta_v,
    )


def test_transfer_time_is_positive():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    result = hohmann_transfer(initial_radius, final_radius)

    assert result.transfer_time > 0


def test_known_earth_orbit_transfer():
    """Check a 400 km to 800 km transfer against an independent calculation."""

    r1 = EARTH_RADIUS + 400_000
    r2 = EARTH_RADIUS + 800_000

    a = (r1 + r2) / 2

    v1 = math.sqrt(EARTH_MU / r1)
    v2 = math.sqrt(EARTH_MU / r2)

    v_transfer_1 = math.sqrt(
        EARTH_MU * (2 / r1 - 1 / a)
    )

    v_transfer_2 = math.sqrt(
        EARTH_MU * (2 / r2 - 1 / a)
    )

    expected_dv1 = abs(v_transfer_1 - v1)
    expected_dv2 = abs(v2 - v_transfer_2)

    result = hohmann_transfer(r1, r2)

    assert math.isclose(
        result.first_burn_delta_v,
        expected_dv1,
    )

    assert math.isclose(
        result.second_burn_delta_v,
        expected_dv2,
    )