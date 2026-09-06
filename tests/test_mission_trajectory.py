import math

import pytest

from astra.physics.constants import EARTH_RADIUS
from astra.physics.orbital import circular_orbital_velocity
from astra.simulation.mission_trajectory import (
    simulate_continuous_hohmann,
)


def test_continuous_transfer_has_two_burns():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    trajectory = simulate_continuous_hohmann(
        initial_radius,
        final_radius,
        dt=10,
    )

    assert len(trajectory.burns) == 2


def test_raising_transfer_uses_prograde_burns():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    trajectory = simulate_continuous_hohmann(
        initial_radius,
        final_radius,
        dt=10,
    )

    assert trajectory.burns[0].direction == "prograde"
    assert trajectory.burns[1].direction == "prograde"


def test_lowering_transfer_uses_retrograde_burns():
    initial_radius = EARTH_RADIUS + 800_000
    final_radius = EARTH_RADIUS + 400_000

    trajectory = simulate_continuous_hohmann(
        initial_radius,
        final_radius,
        dt=10,
    )

    assert trajectory.burns[0].direction == "retrograde"
    assert trajectory.burns[1].direction == "retrograde"


def test_first_burn_occurs_at_start():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    trajectory = simulate_continuous_hohmann(
        initial_radius,
        final_radius,
        dt=10,
    )

    first_burn = trajectory.burns[0]

    assert first_burn.time == pytest.approx(0.0)
    assert first_burn.delta_v > 0


def test_second_burn_occurs_at_transfer_time():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    trajectory = simulate_continuous_hohmann(
        initial_radius,
        final_radius,
        dt=10,
    )

    second_burn = trajectory.burns[1]

    assert second_burn.time > 0
    assert second_burn.delta_v > 0


def test_raising_transfer_reaches_target_radius():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    trajectory = simulate_continuous_hohmann(
        initial_radius,
        final_radius,
        dt=10,
    )

    second_burn = trajectory.burns[1]

    radius = math.hypot(
        second_burn.state_after.x,
        second_burn.state_after.y,
    )

    assert radius == pytest.approx(
        final_radius,
        rel=1e-5,
    )


def test_lowering_transfer_reaches_target_radius():
    initial_radius = EARTH_RADIUS + 800_000
    final_radius = EARTH_RADIUS + 400_000

    trajectory = simulate_continuous_hohmann(
        initial_radius,
        final_radius,
        dt=10,
    )

    second_burn = trajectory.burns[1]

    radius = math.hypot(
        second_burn.state_after.x,
        second_burn.state_after.y,
    )

    assert radius == pytest.approx(
        final_radius,
        rel=1e-5,
    )


def test_final_speed_matches_target_circular_velocity():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    trajectory = simulate_continuous_hohmann(
        initial_radius,
        final_radius,
        dt=10,
    )

    second_burn = trajectory.burns[1]

    speed = math.hypot(
        second_burn.state_after.vx,
        second_burn.state_after.vy,
    )

    expected_speed = circular_orbital_velocity(
        final_radius
    )

    assert speed == pytest.approx(
        expected_speed,
        rel=1e-5,
    )


def test_mission_contains_multiple_states():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    trajectory = simulate_continuous_hohmann(
        initial_radius,
        final_radius,
        dt=10,
    )

    assert len(trajectory.times) > 100
    assert len(trajectory.states) == len(
        trajectory.times
    )


def test_invalid_radius_is_rejected():
    with pytest.raises(ValueError):
        simulate_continuous_hohmann(
            0,
            EARTH_RADIUS + 800_000,
        )


def test_equal_orbits_are_rejected():
    radius = EARTH_RADIUS + 400_000

    with pytest.raises(ValueError):
        simulate_continuous_hohmann(
            radius,
            radius,
        )


def test_invalid_timestep_is_rejected():
    with pytest.raises(ValueError):
        simulate_continuous_hohmann(
            EARTH_RADIUS + 400_000,
            EARTH_RADIUS + 800_000,
            dt=0,
        )