"""Tests for ASTRA trajectory-history generation."""

import math

import pytest

from astra.physics.burn_vector import BurnVector
from astra.physics.constants import EARTH_MU
from astra.physics.thrust import ThrustModel
from astra.simulation.propagator_3d_thrust import State3DThrust
from astra.simulation.propagator_3d_thrust_j2 import State3DThrustJ2
from astra.simulation.trajectory_history import (
    TrajectoryHistory,
    TrajectoryPoint,
    simulate_trajectory,
    simulate_trajectory_j2,
)


def circular_state(
    altitude: float = 400_000.0,
    mass: float = 500.0,
) -> State3DThrust:
    """Return a circular equatorial Earth orbit state."""

    radius = 6_371_000.0 + altitude
    velocity = math.sqrt(
        EARTH_MU / radius
    )

    return State3DThrust(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=velocity,
        vz=0.0,
        mass=mass,
    )


def zero_thrust_model() -> ThrustModel:
    """Return a zero-thrust model for pure orbital propagation."""

    return ThrustModel(
        thrust=0.0,
        specific_impulse=300.0,
    )


def test_trajectory_records_initial_state() -> None:
    """The first trajectory point must be the initial state."""

    initial_state = circular_state()

    history = simulate_trajectory(
        initial_state=initial_state,
        duration=10.0,
        timestep=1.0,
        thrust_model=zero_thrust_model(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
    )

    assert history.points[0].time == 0.0
    assert history.initial_state == initial_state


def test_trajectory_reaches_exact_requested_duration() -> None:
    """A non-divisible duration must use a final partial timestep."""

    history = simulate_trajectory(
        initial_state=circular_state(),
        duration=2.5,
        timestep=1.0,
        thrust_model=zero_thrust_model(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
    )

    assert history.final_time == pytest.approx(2.5)
    assert history.times == pytest.approx(
        (0.0, 1.0, 2.0, 2.5)
    )


def test_zero_duration_records_initial_state_only() -> None:
    """A zero-duration trajectory contains exactly one point."""

    initial_state = circular_state()

    history = simulate_trajectory(
        initial_state=initial_state,
        duration=0.0,
        timestep=1.0,
        thrust_model=zero_thrust_model(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
    )

    assert history.point_count == 1
    assert history.final_time == 0.0
    assert history.final_state == initial_state


def test_point_count_for_even_duration() -> None:
    """An evenly divided duration records both endpoints."""

    history = simulate_trajectory(
        initial_state=circular_state(),
        duration=5.0,
        timestep=1.0,
        thrust_model=zero_thrust_model(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
    )

    assert history.point_count == 6


def test_times_are_monotonically_increasing() -> None:
    """Recorded trajectory times must never move backwards."""

    history = simulate_trajectory(
        initial_state=circular_state(),
        duration=5.0,
        timestep=0.75,
        thrust_model=zero_thrust_model(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
    )

    assert all(
        first <= second
        for first, second in zip(
            history.times,
            history.times[1:],
        )
    )


def test_positions_and_velocities_match_states() -> None:
    """Convenience histories must match the underlying states."""

    history = simulate_trajectory(
        initial_state=circular_state(),
        duration=3.0,
        timestep=1.0,
        thrust_model=zero_thrust_model(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
    )

    expected_positions = tuple(
        (
            state.x,
            state.y,
            state.z,
        )
        for state in history.states
    )

    expected_velocities = tuple(
        (
            state.vx,
            state.vy,
            state.vz,
        )
        for state in history.states
    )

    assert history.positions == expected_positions
    assert history.velocities == expected_velocities


def test_masses_are_recorded() -> None:
    """Mass history must expose spacecraft mass at every point."""

    history = simulate_trajectory(
        initial_state=circular_state(mass=500.0),
        duration=10.0,
        timestep=1.0,
        thrust_model=zero_thrust_model(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
    )

    assert all(
        mass == pytest.approx(500.0)
        for mass in history.masses
    )


def test_finite_thrust_changes_mass_history() -> None:
    """Finite thrust must reduce spacecraft mass over the burn."""

    thrust_model = ThrustModel(
        thrust=100.0,
        specific_impulse=300.0,
    )

    history = simulate_trajectory(
        initial_state=circular_state(mass=500.0),
        duration=10.0,
        timestep=1.0,
        thrust_model=thrust_model,
        thrust_direction=BurnVector(0.0, 1.0, 0.0),
        dry_mass=400.0,
    )

    assert history.masses[0] == pytest.approx(500.0)
    assert history.masses[-1] < history.masses[0]


def test_finite_thrust_changes_velocity() -> None:
    """Finite thrust must change the spacecraft velocity."""

    thrust_model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    history = simulate_trajectory(
        initial_state=circular_state(),
        duration=5.0,
        timestep=1.0,
        thrust_model=thrust_model,
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
        dry_mass=400.0,
    )

    initial_velocity = history.velocities[0]
    final_velocity = history.velocities[-1]

    assert final_velocity != initial_velocity


def test_j2_history_uses_j2_state_type() -> None:
    """J2 trajectory history must contain J2-compatible states."""

    history = simulate_trajectory_j2(
        initial_state=circular_state(),
        duration=5.0,
        timestep=1.0,
        thrust_model=zero_thrust_model(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
    )

    assert history.include_j2 is True
    assert all(
        isinstance(
            state,
            State3DThrustJ2,
        )
        for state in history.states
    )


def test_non_j2_history_uses_standard_state_type() -> None:
    """Non-J2 history must contain standard finite-thrust states."""

    history = simulate_trajectory(
        initial_state=circular_state(),
        duration=5.0,
        timestep=1.0,
        thrust_model=zero_thrust_model(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
    )

    assert history.include_j2 is False
    assert all(
        isinstance(
            state,
            State3DThrust,
        )
        for state in history.states
    )


def test_j2_history_preserves_initial_mass() -> None:
    """The J2 trajectory must preserve initial mass with zero thrust."""

    history = simulate_trajectory_j2(
        initial_state=circular_state(mass=750.0),
        duration=10.0,
        timestep=1.0,
        thrust_model=zero_thrust_model(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
    )

    assert history.masses[0] == pytest.approx(750.0)
    assert history.masses[-1] == pytest.approx(750.0)


def test_zero_timestep_is_rejected() -> None:
    """A zero integration timestep must be rejected."""

    with pytest.raises(ValueError, match="timestep"):
        simulate_trajectory(
            initial_state=circular_state(),
            duration=10.0,
            timestep=0.0,
            thrust_model=zero_thrust_model(),
            thrust_direction=BurnVector(1.0, 0.0, 0.0),
        )


def test_negative_duration_is_rejected() -> None:
    """A negative propagation duration must be rejected."""

    with pytest.raises(ValueError, match="duration"):
        simulate_trajectory(
            initial_state=circular_state(),
            duration=-1.0,
            timestep=1.0,
            thrust_model=zero_thrust_model(),
            thrust_direction=BurnVector(1.0, 0.0, 0.0),
        )


def test_zero_burn_direction_is_rejected() -> None:
    """A zero thrust direction must be rejected."""

    with pytest.raises(
        ValueError,
        match="zero vector",
    ):
        simulate_trajectory(
            initial_state=circular_state(),
            duration=1.0,
            timestep=1.0,
            thrust_model=zero_thrust_model(),
            thrust_direction=BurnVector(0.0, 0.0, 0.0),
        )


def test_dry_mass_above_initial_mass_is_rejected() -> None:
    """Dry mass greater than initial mass must be rejected."""

    with pytest.raises(
        ValueError,
        match="exceed initial mass",
    ):
        simulate_trajectory(
            initial_state=circular_state(mass=500.0),
            duration=1.0,
            timestep=1.0,
            thrust_model=zero_thrust_model(),
            thrust_direction=BurnVector(1.0, 0.0, 0.0),
            dry_mass=600.0,
        )


def test_trajectory_history_rejects_empty_points() -> None:
    """TrajectoryHistory must contain at least one point."""

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        TrajectoryHistory(
            points=(),
            timestep=1.0,
            duration=0.0,
            include_j2=False,
        )


def test_trajectory_history_rejects_negative_duration() -> None:
    """TrajectoryHistory must reject negative durations."""

    state = circular_state()

    with pytest.raises(
        ValueError,
        match="duration",
    ):
        TrajectoryHistory(
            points=(
                TrajectoryPoint(
                    time=0.0,
                    state=state,
                ),
            ),
            timestep=1.0,
            duration=-1.0,
            include_j2=False,
        )


def test_trajectory_history_rejects_unordered_points() -> None:
    """TrajectoryHistory must reject backwards time ordering."""

    state = circular_state()

    with pytest.raises(
        ValueError,
        match="ordered by time",
    ):
        TrajectoryHistory(
            points=(
                TrajectoryPoint(
                    time=1.0,
                    state=state,
                ),
                TrajectoryPoint(
                    time=0.0,
                    state=state,
                ),
            ),
            timestep=1.0,
            duration=1.0,
            include_j2=False,
        )


def test_initial_and_final_state_are_accessible() -> None:
    """Initial and final state properties must expose endpoints."""

    history = simulate_trajectory(
        initial_state=circular_state(),
        duration=2.0,
        timestep=1.0,
        thrust_model=zero_thrust_model(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
    )

    assert history.initial_state == history.states[0]
    assert history.final_state == history.states[-1]
