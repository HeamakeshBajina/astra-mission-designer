"""Tests for ASTRA numerical validation and timestep convergence."""

import pytest

from astra.physics.thrust import ThrustModel
from astra.simulation.numerical_validation import (
    ConvergenceResult,
    StateError,
    propagate_to_time,
    propagate_to_time_j2,
    state_error,
    state_error_j2,
    timestep_convergence,
)
from astra.simulation.propagator_3d_thrust import State3DThrust
from astra.simulation.propagator_3d_thrust_j2 import State3DThrustJ2


def make_state() -> State3DThrust:
    return State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=500_000.0,
        vx=0.0,
        vy=7_200.0,
        vz=500.0,
        mass=500.0,
    )


def make_j2_state() -> State3DThrustJ2:
    return State3DThrustJ2(
        x=7_000_000.0,
        y=0.0,
        z=500_000.0,
        vx=0.0,
        vy=7_200.0,
        vz=500.0,
        mass=500.0,
    )


def make_thrust() -> ThrustModel:
    return ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )


def test_state_error_zero_for_identical_states():
    state = make_state()

    error = state_error(state, state)

    assert isinstance(error, StateError)
    assert error.position_error == 0.0
    assert error.velocity_error == 0.0
    assert error.mass_error == 0.0


def test_state_error_detects_position_difference():
    first = make_state()

    second = State3DThrust(
        x=first.x + 10.0,
        y=first.y,
        z=first.z,
        vx=first.vx,
        vy=first.vy,
        vz=first.vz,
        mass=first.mass,
    )

    error = state_error(first, second)

    assert error.position_error == pytest.approx(10.0)
    assert error.velocity_error == 0.0
    assert error.mass_error == 0.0


def test_state_error_detects_velocity_difference():
    first = make_state()

    second = State3DThrust(
        x=first.x,
        y=first.y,
        z=first.z,
        vx=first.vx + 5.0,
        vy=first.vy,
        vz=first.vz,
        mass=first.mass,
    )

    error = state_error(first, second)

    assert error.position_error == 0.0
    assert error.velocity_error == pytest.approx(5.0)


def test_state_error_detects_mass_difference():
    first = make_state()

    second = State3DThrust(
        x=first.x,
        y=first.y,
        z=first.z,
        vx=first.vx,
        vy=first.vy,
        vz=first.vz,
        mass=first.mass - 2.5,
    )

    error = state_error(first, second)

    assert error.mass_error == pytest.approx(2.5)


def test_j2_state_error_zero_for_identical_states():
    state = make_j2_state()

    error = state_error_j2(state, state)

    assert error.position_error == 0.0
    assert error.velocity_error == 0.0
    assert error.mass_error == 0.0


def test_propagate_to_exact_time():
    result = propagate_to_time(
        initial_state=make_state(),
        duration=10.0,
        dt=2.0,
        thrust_model=make_thrust(),
        thrust_direction=(1.0, 0.0, 0.0),
        dry_mass=450.0,
    )

    assert result.mass == pytest.approx(
        500.0 - make_thrust().mass_flow_rate * 10.0
    )


def test_propagate_to_time_handles_non_divisible_timestep():
    result = propagate_to_time(
        initial_state=make_state(),
        duration=10.5,
        dt=2.0,
        thrust_model=make_thrust(),
        thrust_direction=(1.0, 0.0, 0.0),
        dry_mass=450.0,
    )

    expected_mass = (
        500.0
        - make_thrust().mass_flow_rate * 10.5
    )

    assert result.mass == pytest.approx(expected_mass)


def test_propagate_to_time_rejects_invalid_duration():
    with pytest.raises(ValueError):
        propagate_to_time(
            initial_state=make_state(),
            duration=-1.0,
            dt=1.0,
            thrust_model=make_thrust(),
            thrust_direction=(1.0, 0.0, 0.0),
            dry_mass=450.0,
        )


def test_propagate_to_time_rejects_invalid_timestep():
    with pytest.raises(ValueError):
        propagate_to_time(
            initial_state=make_state(),
            duration=10.0,
            dt=0.0,
            thrust_model=make_thrust(),
            thrust_direction=(1.0, 0.0, 0.0),
            dry_mass=450.0,
        )


def test_j2_propagation_to_exact_time():
    result = propagate_to_time_j2(
        initial_state=make_j2_state(),
        duration=10.5,
        dt=2.0,
        thrust_model=make_thrust(),
        thrust_direction=(0.0, 0.0, 1.0),
        dry_mass=450.0,
    )

    expected_mass = (
        500.0
        - make_thrust().mass_flow_rate * 10.5
    )

    assert result.mass == pytest.approx(expected_mass)


def test_convergence_result_is_created():
    result = timestep_convergence(
        propagate=lambda dt: propagate_to_time(
            initial_state=make_state(),
            duration=10.0,
            dt=dt,
            thrust_model=make_thrust(),
            thrust_direction=(1.0, 0.0, 0.0),
            dry_mass=450.0,
        ),
        coarse_dt=2.0,
        medium_dt=1.0,
        fine_dt=0.5,
        error_function=lambda first, second:
            state_error(first, second).position_error,
        tolerance=100.0,
    )

    assert isinstance(result, ConvergenceResult)
    assert result.coarse_error >= 0.0
    assert result.medium_error >= 0.0


def test_smaller_timestep_reduces_error():
    result = timestep_convergence(
        propagate=lambda dt: propagate_to_time(
            initial_state=make_state(),
            duration=20.0,
            dt=dt,
            thrust_model=make_thrust(),
            thrust_direction=(1.0, 0.0, 0.0),
            dry_mass=450.0,
        ),
        coarse_dt=4.0,
        medium_dt=2.0,
        fine_dt=1.0,
        error_function=lambda first, second:
            state_error(first, second).position_error,
        tolerance=100.0,
    )

    assert result.medium_error < result.coarse_error


def test_convergence_ratio_is_positive():
    result = timestep_convergence(
        propagate=lambda dt: propagate_to_time(
            initial_state=make_state(),
            duration=20.0,
            dt=dt,
            thrust_model=make_thrust(),
            thrust_direction=(1.0, 0.0, 0.0),
            dry_mass=450.0,
        ),
        coarse_dt=4.0,
        medium_dt=2.0,
        fine_dt=1.0,
        error_function=lambda first, second:
            state_error(first, second).position_error,
        tolerance=100.0,
    )

    assert result.convergence_ratio > 1.0


def test_convergence_can_be_reported_as_pass():
    result = timestep_convergence(
        propagate=lambda dt: propagate_to_time(
            initial_state=make_state(),
            duration=10.0,
            dt=dt,
            thrust_model=make_thrust(),
            thrust_direction=(1.0, 0.0, 0.0),
            dry_mass=450.0,
        ),
        coarse_dt=2.0,
        medium_dt=1.0,
        fine_dt=0.5,
        error_function=lambda first, second:
            state_error(first, second).position_error,
        tolerance=100.0,
    )

    assert result.converged is True


def test_convergence_rejects_bad_timestep_order():
    with pytest.raises(ValueError):
        timestep_convergence(
            propagate=lambda dt: dt,
            coarse_dt=1.0,
            medium_dt=2.0,
            fine_dt=0.5,
            error_function=lambda first, second: abs(first - second),
        )


def test_convergence_rejects_invalid_tolerance():
    with pytest.raises(ValueError):
        timestep_convergence(
            propagate=lambda dt: dt,
            coarse_dt=2.0,
            medium_dt=1.0,
            fine_dt=0.5,
            error_function=lambda first, second: abs(first - second),
            tolerance=0.0,
        )


def test_convergence_rejects_invalid_timestep():
    with pytest.raises(ValueError):
        timestep_convergence(
            propagate=lambda dt: dt,
            coarse_dt=0.0,
            medium_dt=1.0,
            fine_dt=0.5,
            error_function=lambda first, second: abs(first - second),
        )


def test_j2_convergence_study():
    result = timestep_convergence(
        propagate=lambda dt: propagate_to_time_j2(
            initial_state=make_j2_state(),
            duration=20.0,
            dt=dt,
            thrust_model=ThrustModel(
                thrust=0.0,
                specific_impulse=300.0,
            ),
            thrust_direction=(1.0, 0.0, 0.0),
            dry_mass=450.0,
        ),
        coarse_dt=4.0,
        medium_dt=2.0,
        fine_dt=1.0,
        error_function=lambda first, second:
            state_error_j2(first, second).position_error,
        tolerance=100.0,
    )

    assert result.coarse_error >= result.medium_error
    assert result.convergence_ratio > 1.0
