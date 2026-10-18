"""Independent analytical benchmarks for ASTRA orbital mechanics."""

import math

import pytest

from astra.physics.constants import EARTH_MU, EARTH_RADIUS
from astra.physics.orbital import (
    circular_orbital_velocity,
    escape_velocity,
    orbital_period,
)
from astra.physics.transfers import hohmann_transfer


# These benchmark equations are written independently of ASTRA's
# implementation functions. SI units are used throughout.
def reference_circular_speed(mu: float, radius: float) -> float:
    return math.sqrt(mu / radius)


def reference_escape_speed(mu: float, radius: float) -> float:
    return math.sqrt(2.0 * mu / radius)


def reference_orbital_period(mu: float, radius: float) -> float:
    return 2.0 * math.pi * math.sqrt(radius**3 / mu)


def reference_hohmann_delta_v(
    mu: float,
    initial_radius: float,
    final_radius: float,
) -> tuple[float, float]:
    transfer_semimajor_axis = (initial_radius + final_radius) / 2.0

    initial_circular_speed = math.sqrt(mu / initial_radius)
    final_circular_speed = math.sqrt(mu / final_radius)

    transfer_speed_at_initial = math.sqrt(
        mu * (2.0 / initial_radius - 1.0 / transfer_semimajor_axis)
    )
    transfer_speed_at_final = math.sqrt(
        mu * (2.0 / final_radius - 1.0 / transfer_semimajor_axis)
    )

    first_burn = abs(transfer_speed_at_initial - initial_circular_speed)
    second_burn = abs(final_circular_speed - transfer_speed_at_final)
    return first_burn, second_burn


@pytest.mark.parametrize("altitude_m", [200_000.0, 400_000.0, 800_000.0, 2_000_000.0])
def test_circular_speed_matches_independent_equation(altitude_m):
    radius = EARTH_RADIUS + altitude_m
    expected = reference_circular_speed(EARTH_MU, radius)

    assert circular_orbital_velocity(radius) == pytest.approx(
        expected, rel=1e-12
    )


@pytest.mark.parametrize("altitude_m", [200_000.0, 400_000.0, 800_000.0, 2_000_000.0])
def test_escape_speed_matches_independent_equation(altitude_m):
    radius = EARTH_RADIUS + altitude_m
    expected = reference_escape_speed(EARTH_MU, radius)

    assert escape_velocity(radius) == pytest.approx(
        expected, rel=1e-12
    )


@pytest.mark.parametrize("altitude_m", [200_000.0, 400_000.0, 800_000.0, 2_000_000.0])
def test_orbital_period_matches_independent_equation(altitude_m):
    radius = EARTH_RADIUS + altitude_m
    expected = reference_orbital_period(EARTH_MU, radius)

    assert orbital_period(radius) == pytest.approx(
        expected, rel=1e-12
    )


@pytest.mark.parametrize(
    ("initial_altitude_m", "final_altitude_m"),
    [
        (200_000.0, 400_000.0),
        (400_000.0, 800_000.0),
        (400_000.0, 35_786_000.0),
        (800_000.0, 400_000.0),
    ],
)
def test_hohmann_transfer_matches_independent_equation(
    initial_altitude_m,
    final_altitude_m,
):
    initial_radius = EARTH_RADIUS + initial_altitude_m
    final_radius = EARTH_RADIUS + final_altitude_m

    expected_first, expected_second = reference_hohmann_delta_v(
        EARTH_MU,
        initial_radius,
        final_radius,
    )

    result = hohmann_transfer(initial_radius, final_radius)

    assert result.first_burn_delta_v == pytest.approx(
        expected_first, rel=1e-10, abs=1e-10
    )
    assert result.second_burn_delta_v == pytest.approx(
        expected_second, rel=1e-10, abs=1e-10
    )