"""Tests for ASTRA's three-dimensional orbital propagator."""

import math

import pytest

from astra.physics.constants import EARTH_MU
from astra.simulation.propagator_3d import (
    State3D,
    gravitational_acceleration_3d,
    rk4_step_3d,
)


def test_gravity_points_toward_earth_center():
    """Gravity should point toward the origin."""

    ax, ay, az = gravitational_acceleration_3d(
        7_000_000.0,
        0.0,
        0.0,
    )

    assert ax < 0
    assert ay == pytest.approx(0.0)
    assert az == pytest.approx(0.0)


def test_gravity_has_correct_inverse_square_magnitude():
    """Gravity magnitude should follow mu / r^2."""

    x = 7_000_000.0
    y = 0.0
    z = 0.0

    ax, ay, az = gravitational_acceleration_3d(x, y, z)

    acceleration = math.sqrt(
        ax**2 + ay**2 + az**2
    )

    expected = EARTH_MU / x**2

    assert acceleration == pytest.approx(
        expected,
        rel=1e-12,
    )


def test_gravity_works_in_three_dimensions():
    """Gravity should correctly act along all three axes."""

    ax, ay, az = gravitational_acceleration_3d(
        0.0,
        0.0,
        7_000_000.0,
    )

    assert ax == pytest.approx(0.0)
    assert ay == pytest.approx(0.0)
    assert az < 0


def test_gravity_rejects_center_of_earth():
    """The origin should be rejected because gravity is undefined there."""

    with pytest.raises(ValueError):
        gravitational_acceleration_3d(
            0.0,
            0.0,
            0.0,
        )


def test_rk4_step_updates_position():
    """RK4 should advance position using the spacecraft velocity."""

    state = State3D(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
    )

    next_state = rk4_step_3d(
        state,
        dt=1.0,
    )

    assert next_state.x != state.x
    assert next_state.y > state.y
    assert next_state.z == pytest.approx(0.0)


def test_planar_orbit_remains_planar():
    """A state with zero z and vz should remain in the XY plane."""

    state = State3D(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_546.0,
        vz=0.0,
    )

    for _ in range(100):
        state = rk4_step_3d(
            state,
            dt=10.0,
        )

    assert state.z == pytest.approx(0.0)
    assert state.vz == pytest.approx(0.0)


def test_3d_orbit_preserves_reasonable_speed():
    """A short circular-orbit propagation should remain numerically stable."""

    radius = 7_000_000.0
    circular_speed = math.sqrt(
        EARTH_MU / radius
    )

    state = State3D(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=circular_speed,
        vz=0.0,
    )

    initial_speed = math.sqrt(
        state.vx**2
        + state.vy**2
        + state.vz**2
    )

    for _ in range(100):
        state = rk4_step_3d(
            state,
            dt=10.0,
        )

    final_speed = math.sqrt(
        state.vx**2
        + state.vy**2
        + state.vz**2
    )

    assert final_speed == pytest.approx(
        initial_speed,
        rel=1e-6,
    )