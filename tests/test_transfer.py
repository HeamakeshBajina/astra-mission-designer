import math

import pytest

from astra.physics.constants import EARTH_RADIUS
from astra.simulation.transfer import simulate_hohmann_transfer


def test_transfer_simulation_creates_three_trajectories():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    result = simulate_hohmann_transfer(
        initial_radius,
        final_radius,
        dt=10,
    )

    assert result.initial_orbit is not None
    assert result.transfer_orbit is not None
    assert result.final_orbit is not None


def test_transfer_orbit_starts_at_initial_radius():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    result = simulate_hohmann_transfer(
        initial_radius,
        final_radius,
        dt=10,
    )

    state = result.transfer_orbit.states[0]

    radius = math.hypot(
        state.x,
        state.y,
    )

    assert math.isclose(
        radius,
        initial_radius,
        rel_tol=1e-10,
    )


def test_transfer_orbit_reaches_approximately_final_radius():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    result = simulate_hohmann_transfer(
        initial_radius,
        final_radius,
        dt=10,
    )

    state = result.transfer_orbit.states[-1]

    radius = math.hypot(
        state.x,
        state.y,
    )

    assert math.isclose(
        radius,
        final_radius,
        rel_tol=1e-5,
    )


def test_transfer_simulation_rejects_equal_orbits():
    radius = EARTH_RADIUS + 400_000

    with pytest.raises(ValueError):
        simulate_hohmann_transfer(
            radius,
            radius,
        )


def test_transfer_simulation_rejects_invalid_timestep():
    initial_radius = EARTH_RADIUS + 400_000
    final_radius = EARTH_RADIUS + 800_000

    with pytest.raises(ValueError):
        simulate_hohmann_transfer(
            initial_radius,
            final_radius,
            dt=0,
        )