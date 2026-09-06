import math

import pytest

from astra.physics.constants import EARTH_MU, EARTH_RADIUS
from astra.physics.orbital import circular_orbital_velocity
from astra.simulation.propagator import (
    State,
    gravitational_acceleration,
    rk4_step,
)


def test_gravity_points_toward_earth():
    ax, ay = gravitational_acceleration(
        EARTH_RADIUS,
        0,
    )

    assert ax < 0
    assert math.isclose(ay, 0.0)


def test_gravity_magnitude():
    ax, ay = gravitational_acceleration(
        EARTH_RADIUS,
        0,
    )

    acceleration = math.sqrt(ax**2 + ay**2)

    expected = EARTH_MU / EARTH_RADIUS**2

    assert math.isclose(
        acceleration,
        expected,
        rel_tol=1e-10,
    )


def test_invalid_position():
    with pytest.raises(ValueError):
        gravitational_acceleration(0, 0)


def test_rk4_step_changes_position():
    velocity = circular_orbital_velocity(EARTH_RADIUS)

    initial = State(
        x=EARTH_RADIUS,
        y=0,
        vx=0,
        vy=velocity,
    )

    result = rk4_step(initial, 1.0)

    assert result.x != initial.x
    assert result.y > initial.y


def test_circular_orbit_speed_remains_stable_for_small_step():
    velocity = circular_orbital_velocity(EARTH_RADIUS)

    initial = State(
        x=EARTH_RADIUS,
        y=0,
        vx=0,
        vy=velocity,
    )

    result = rk4_step(initial, 1.0)

    initial_speed = math.sqrt(
        initial.vx**2 + initial.vy**2
    )

    final_speed = math.sqrt(
        result.vx**2 + result.vy**2
    )

    assert math.isclose(
        final_speed,
        initial_speed,
        rel_tol=1e-8,
    )