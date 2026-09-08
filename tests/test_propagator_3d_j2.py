"""Tests for ASTRA's 3D J2-perturbed propagator."""

import math

import pytest

from astra.physics.constants import EARTH_MU
from astra.physics.j2 import EARTH_J2
from astra.simulation.propagator_3d_j2 import (
    State3DJ2,
    rk4_step_3d_j2,
    total_acceleration_3d_j2,
)


def vector_magnitude(
    vector: tuple[float, float, float],
) -> float:
    """Return the magnitude of a 3D vector."""

    return math.sqrt(
        sum(component**2 for component in vector)
    )


def orbital_radius(state: State3DJ2) -> float:
    """Return distance from Earth's center."""

    return math.sqrt(
        state.x**2
        + state.y**2
        + state.z**2
    )


def propagate(
    state: State3DJ2,
    duration: float,
    dt: float,
) -> State3DJ2:
    """Propagate a state for a specified duration."""

    steps = int(duration / dt)

    for _ in range(steps):
        state = rk4_step_3d_j2(
            state,
            dt,
        )

    return state


def test_total_acceleration_points_toward_earth_on_x_axis():
    """Total acceleration should point inward on the x-axis."""

    ax, ay, az = total_acceleration_3d_j2(
        7_000_000.0,
        0.0,
        0.0,
    )

    assert ax < 0
    assert ay == pytest.approx(0.0)
    assert az == pytest.approx(0.0)


def test_j2_perturbation_is_small_relative_to_gravity():
    """J2 should remain a small perturbation to central gravity."""

    radius = 7_000_000.0

    total = total_acceleration_3d_j2(
        radius,
        0.0,
        0.0,
    )

    central = EARTH_MU / radius**2

    total_magnitude = vector_magnitude(total)

    # The J2 perturbation should be small compared with
    # Earth's central gravitational acceleration.
    assert total_magnitude > 0
    assert total_magnitude / central < 1.01


def test_j2_enabled_propagator_updates_state():
    """The J2 propagator should produce a new spacecraft state."""

    state = State3DJ2(
        x=7_000_000.0,
        y=0.0,
        z=1_000_000.0,
        vx=0.0,
        vy=7_400.0,
        vz=500.0,
    )

    next_state = rk4_step_3d_j2(
        state,
        dt=1.0,
    )

    assert next_state != state


def test_j2_propagator_preserves_three_dimensional_motion():
    """An inclined orbit should continue to have non-zero z motion."""

    radius = 7_000_000.0
    speed = math.sqrt(EARTH_MU / radius)
    inclination = math.radians(45.0)

    state = State3DJ2(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=speed * math.cos(inclination),
        vz=speed * math.sin(inclination),
    )

    state = propagate(
        state,
        duration=1800.0,
        dt=10.0,
    )

    assert abs(state.z) > 1_000.0
    assert abs(state.vz) > 0.1


def test_j2_propagator_radius_remains_bounded():
    """A short low-Earth orbit should remain physically bounded."""

    radius = 7_000_000.0
    speed = math.sqrt(EARTH_MU / radius)

    state = State3DJ2(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=speed,
        vz=0.0,
    )

    state = propagate(
        state,
        duration=3600.0,
        dt=10.0,
    )

    final_radius = orbital_radius(state)

    assert 6_900_000.0 < final_radius < 7_100_000.0


def test_j2_acceleration_changes_with_latitude():
    """J2 acceleration should differ between latitudes."""

    radius = 7_000_000.0

    equatorial = total_acceleration_3d_j2(
        radius,
        0.0,
        0.0,
    )

    off_equator = total_acceleration_3d_j2(
        radius / math.sqrt(2),
        0.0,
        radius / math.sqrt(2),
    )

    assert equatorial != off_equator


def test_invalid_timestep_is_rejected():
    """Non-positive timesteps should be rejected."""

    state = State3DJ2(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
    )

    with pytest.raises(ValueError):
        rk4_step_3d_j2(
            state,
            dt=0.0,
        )


def test_center_position_is_rejected():
    """The Earth's center should be rejected."""

    with pytest.raises(ValueError):
        total_acceleration_3d_j2(
            0.0,
            0.0,
            0.0,
        )