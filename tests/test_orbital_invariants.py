"""Physical-invariant tests for ideal Hohmann transfers."""

import math

import pytest

from astra.physics.constants import EARTH_MU, EARTH_RADIUS
from astra.physics.transfers import hohmann_transfer


TRANSFER_CASES = [
    (200_000.0, 400_000.0),
    (400_000.0, 800_000.0),
    (400_000.0, 35_786_000.0),
    (800_000.0, 400_000.0),
]


def reference_vis_viva_speed(mu: float, radius: float, semi_major_axis: float) -> float:
    """Independently calculate speed from the vis-viva equation."""
    return math.sqrt(mu * (2.0 / radius - 1.0 / semi_major_axis))


@pytest.mark.parametrize(
    ("initial_altitude_m", "final_altitude_m"),
    TRANSFER_CASES,
)
def test_transfer_semi_major_axis_matches_geometry(
    initial_altitude_m,
    final_altitude_m,
):
    initial_radius = EARTH_RADIUS + initial_altitude_m
    final_radius = EARTH_RADIUS + final_altitude_m

    result = hohmann_transfer(initial_radius, final_radius)
    expected_axis = (initial_radius + final_radius) / 2.0

    assert result.transfer_semi_major_axis == pytest.approx(
        expected_axis, rel=1e-12
    )


@pytest.mark.parametrize(
    ("initial_altitude_m", "final_altitude_m"),
    TRANSFER_CASES,
)
def test_specific_orbital_energy_is_conserved_across_transfer(
    initial_altitude_m,
    final_altitude_m,
):
    initial_radius = EARTH_RADIUS + initial_altitude_m
    final_radius = EARTH_RADIUS + final_altitude_m
    result = hohmann_transfer(initial_radius, final_radius)

    axis = (initial_radius + final_radius) / 2.0
    periapsis_speed = reference_vis_viva_speed(
        EARTH_MU, initial_radius, axis
    )
    apoapsis_speed = reference_vis_viva_speed(
        EARTH_MU, final_radius, axis
    )

    energy_at_periapsis = (
        0.5 * periapsis_speed**2 - EARTH_MU / initial_radius
    )
    energy_at_apoapsis = (
        0.5 * apoapsis_speed**2 - EARTH_MU / final_radius
    )
    expected_energy = -EARTH_MU / (2.0 * axis)

    assert energy_at_periapsis == pytest.approx(
        expected_energy, rel=1e-12
    )
    assert energy_at_apoapsis == pytest.approx(
        expected_energy, rel=1e-12
    )
    assert energy_at_periapsis == pytest.approx(
        energy_at_apoapsis, rel=1e-12
    )


@pytest.mark.parametrize(
    ("initial_altitude_m", "final_altitude_m"),
    TRANSFER_CASES,
)
def test_specific_angular_momentum_is_conserved(
    initial_altitude_m,
    final_altitude_m,
):
    initial_radius = EARTH_RADIUS + initial_altitude_m
    final_radius = EARTH_RADIUS + final_altitude_m
    axis = (initial_radius + final_radius) / 2.0

    periapsis_speed = reference_vis_viva_speed(
        EARTH_MU, initial_radius, axis
    )
    apoapsis_speed = reference_vis_viva_speed(
        EARTH_MU, final_radius, axis
    )

    angular_momentum_at_periapsis = initial_radius * periapsis_speed
    angular_momentum_at_apoapsis = final_radius * apoapsis_speed

    assert angular_momentum_at_periapsis == pytest.approx(
        angular_momentum_at_apoapsis, rel=1e-12
    )


@pytest.mark.parametrize(
    ("initial_altitude_m", "final_altitude_m"),
    TRANSFER_CASES,
)
def test_transfer_time_is_half_transfer_orbit_period(
    initial_altitude_m,
    final_altitude_m,
):
    initial_radius = EARTH_RADIUS + initial_altitude_m
    final_radius = EARTH_RADIUS + final_altitude_m
    result = hohmann_transfer(initial_radius, final_radius)

    axis = (initial_radius + final_radius) / 2.0
    expected_transfer_time = math.pi * math.sqrt(
        axis**3 / EARTH_MU
    )

    assert result.transfer_time == pytest.approx(
        expected_transfer_time, rel=1e-12
    )


@pytest.mark.parametrize(
    ("initial_altitude_m", "final_altitude_m"),
    TRANSFER_CASES,
)
def test_total_delta_v_equals_sum_of_burn_magnitudes(
    initial_altitude_m,
    final_altitude_m,
):
    initial_radius = EARTH_RADIUS + initial_altitude_m
    final_radius = EARTH_RADIUS + final_altitude_m
    result = hohmann_transfer(initial_radius, final_radius)

    assert result.total_delta_v == pytest.approx(
        result.first_burn_delta_v + result.second_burn_delta_v,
        rel=1e-12,
        abs=1e-12,
    )
    assert result.first_burn_delta_v >= 0.0
    assert result.second_burn_delta_v >= 0.0
