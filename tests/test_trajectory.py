import math

import pytest

from astra.physics.constants import EARTH_RADIUS
from astra.physics.orbital import circular_orbital_velocity
from astra.simulation.propagator import State
from astra.simulation.trajectory import propagate_trajectory


def test_trajectory_contains_initial_state():
    velocity = circular_orbital_velocity(EARTH_RADIUS)

    initial = State(
        x=EARTH_RADIUS,
        y=0,
        vx=0,
        vy=velocity,
    )

    trajectory = propagate_trajectory(
        initial_state=initial,
        duration=10,
        dt=1,
    )

    assert trajectory.states[0] == initial
    assert trajectory.times[0] == 0


def test_trajectory_has_expected_number_of_steps():
    velocity = circular_orbital_velocity(EARTH_RADIUS)

    initial = State(
        x=EARTH_RADIUS,
        y=0,
        vx=0,
        vy=velocity,
    )

    trajectory = propagate_trajectory(
        initial_state=initial,
        duration=10,
        dt=1,
    )

    assert len(trajectory.states) == 11
    assert len(trajectory.times) == 11


def test_trajectory_time_is_monotonic():
    velocity = circular_orbital_velocity(EARTH_RADIUS)

    initial = State(
        x=EARTH_RADIUS,
        y=0,
        vx=0,
        vy=velocity,
    )

    trajectory = propagate_trajectory(
        initial_state=initial,
        duration=10,
        dt=1,
    )

    assert trajectory.times == sorted(trajectory.times)


def test_trajectory_reaches_final_time():
    velocity = circular_orbital_velocity(EARTH_RADIUS)

    initial = State(
        x=EARTH_RADIUS,
        y=0,
        vx=0,
        vy=velocity,
    )

    trajectory = propagate_trajectory(
        initial_state=initial,
        duration=10,
        dt=1,
    )

    assert math.isclose(trajectory.times[-1], 10)


def test_trajectory_changes_position():
    velocity = circular_orbital_velocity(EARTH_RADIUS)

    initial = State(
        x=EARTH_RADIUS,
        y=0,
        vx=0,
        vy=velocity,
    )

    trajectory = propagate_trajectory(
        initial_state=initial,
        duration=10,
        dt=1,
    )

    final = trajectory.states[-1]

    assert final.y > initial.y


def test_invalid_duration():
    velocity = circular_orbital_velocity(EARTH_RADIUS)

    initial = State(
        x=EARTH_RADIUS,
        y=0,
        vx=0,
        vy=velocity,
    )

    with pytest.raises(ValueError):
        propagate_trajectory(initial, 0, 1)


def test_invalid_timestep():
    velocity = circular_orbital_velocity(EARTH_RADIUS)

    initial = State(
        x=EARTH_RADIUS,
        y=0,
        vx=0,
        vy=velocity,
    )

    with pytest.raises(ValueError):
        propagate_trajectory(initial, 10, 0)
