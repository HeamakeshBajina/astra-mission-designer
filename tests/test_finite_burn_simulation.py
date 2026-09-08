"""Tests for ASTRA's multi-step finite-burn simulation."""

import pytest

from astra.physics.thrust import ThrustModel
from astra.simulation.finite_burn import FiniteBurn
from astra.simulation.finite_burn_simulation import (
    BurnSimulation,
    simulate_burn,
    simulate_finite_burn,
)
from astra.simulation.propagator_3d_thrust import State3DThrust


def make_state() -> State3DThrust:
    """Create a representative orbital state."""
    return State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=500.0,
    )


def make_burn(duration: float = 10.0) -> FiniteBurn:
    """Create a representative finite burn."""
    return FiniteBurn(
        thrust_model=ThrustModel(
            thrust=1000.0,
            specific_impulse=300.0,
        ),
        duration=duration,
        dry_mass=450.0,
    )


def test_simulate_burn_returns_burn_simulation():
    result = simulate_burn(
        make_state(), make_burn(), (1.0, 0.0, 0.0), dt=1.0
    )
    assert isinstance(result, BurnSimulation)


def test_initial_state_is_preserved():
    result = simulate_burn(
        make_state(), make_burn(), (1.0, 0.0, 0.0), dt=1.0
    )
    assert result.initial_state == make_state()


def test_final_state_is_last_trajectory_state():
    result = simulate_burn(
        make_state(), make_burn(), (1.0, 0.0, 0.0), dt=1.0
    )
    assert result.final_state == result.states[-1]


def test_trajectory_contains_expected_number_of_states():
    result = simulate_burn(
        make_state(), make_burn(10.0), (1.0, 0.0, 0.0), dt=1.0
    )
    assert len(result.states) == 11


def test_mass_decreases_monotonically():
    result = simulate_burn(
        make_state(), make_burn(10.0), (1.0, 0.0, 0.0), dt=1.0
    )

    masses = [state.mass for state in result.states]

    assert all(
        later <= earlier
        for earlier, later in zip(masses, masses[1:])
    )


def test_final_mass_matches_analytical_solution():
    initial = make_state()
    burn = make_burn(10.0)

    result = simulate_burn(
        initial, burn, (1.0, 0.0, 0.0), dt=1.0
    )

    assert result.final_state.mass == pytest.approx(
        burn.final_mass(initial.mass)
    )


def test_final_mass_remains_above_dry_mass():
    result = simulate_burn(
        make_state(), make_burn(10.0), (1.0, 0.0, 0.0), dt=1.0
    )

    assert result.final_state.mass >= make_burn().dry_mass


def test_position_changes():
    result = simulate_burn(
        make_state(), make_burn(), (1.0, 0.0, 0.0), dt=1.0
    )

    assert result.final_state.x != result.initial_state.x
    assert result.final_state.y != result.initial_state.y


def test_velocity_changes():
    result = simulate_burn(
        make_state(), make_burn(), (1.0, 0.0, 0.0), dt=1.0
    )

    assert result.final_state.vx != result.initial_state.vx
    assert result.final_state.vy != result.initial_state.vy


def test_partial_final_timestep_is_supported():
    initial = make_state()
    burn = make_burn(10.5)

    result = simulate_burn(
        initial, burn, (1.0, 0.0, 0.0), dt=2.0
    )

    assert result.final_state.mass == pytest.approx(
        burn.final_mass(initial.mass)
    )


def test_zero_duration_returns_one_state():
    result = simulate_burn(
        make_state(), make_burn(0.0), (1.0, 0.0, 0.0), dt=1.0
    )

    assert len(result.states) == 1
    assert result.final_state == result.initial_state


def test_invalid_timestep_is_rejected():
    with pytest.raises(ValueError):
        simulate_burn(
            make_state(), make_burn(), (1.0, 0.0, 0.0), dt=0.0
        )


def test_insufficient_propellant_is_rejected():
    # 1000 N / (300 s * g0) ≈ 0.340 kg/s.
    # 200 s requires ≈ 67.99 kg, but only 50 kg is available.
    burn = make_burn(200.0)

    with pytest.raises(ValueError):
        simulate_burn(
            make_state(), burn, (1.0, 0.0, 0.0), dt=1.0
        )


def test_backward_compatible_function_returns_list():
    states = simulate_finite_burn(
        make_state(), make_burn(), (1.0, 0.0, 0.0), dt=1.0
    )

    assert isinstance(states, list)
    assert len(states) == 11


def test_simulation_duration_property():
    result = simulate_burn(
        make_state(), make_burn(10.0), (1.0, 0.0, 0.0), dt=1.0
    )

    assert result.duration == pytest.approx(10.0)


def test_smaller_timestep_produces_same_final_mass():
    initial = make_state()
    burn = make_burn(10.0)

    coarse = simulate_burn(
        initial, burn, (1.0, 0.0, 0.0), dt=1.0
    )

    fine = simulate_burn(
        initial, burn, (1.0, 0.0, 0.0), dt=0.5
    )

    assert fine.final_state.mass == pytest.approx(
        coarse.final_state.mass
    )
