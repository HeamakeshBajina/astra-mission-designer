"""Tests for ASTRA's 3D finite-thrust propagator."""

import pytest

from astra.physics.constants import EARTH_MU
from astra.physics.thrust import ThrustModel
from astra.simulation.propagator_3d_thrust import (
    State3DThrust,
    rk4_step_thrust,
)


def test_zero_thrust_keeps_mass_constant():
    """Zero thrust should produce no mass loss."""

    model = ThrustModel(
        thrust=0.0,
        specific_impulse=300.0,
    )

    state = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=500.0,
    )

    result = rk4_step_thrust(
        state,
        dt=1.0,
        thrust_model=model,
        thrust_direction=(1.0, 0.0, 0.0),
    )

    assert result.mass == pytest.approx(
        state.mass
    )


def test_thrust_reduces_mass():
    """Finite thrust should reduce spacecraft mass."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    state = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=500.0,
    )

    result = rk4_step_thrust(
        state,
        dt=10.0,
        thrust_model=model,
        thrust_direction=(1.0, 0.0, 0.0),
    )

    assert result.mass < state.mass


def test_thrust_changes_velocity():
    """Thrust should contribute acceleration in its commanded direction."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    state = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=500.0,
    )

    result_with_thrust = rk4_step_thrust(
        state,
        dt=1.0,
        thrust_model=model,
        thrust_direction=(1.0, 0.0, 0.0),
    )

    zero_thrust_model = ThrustModel(
        thrust=0.0,
        specific_impulse=300.0,
    )

    result_without_thrust = rk4_step_thrust(
        state,
        dt=1.0,
        thrust_model=zero_thrust_model,
        thrust_direction=(1.0, 0.0, 0.0),
    )

    assert (
        result_with_thrust.vx
        > result_without_thrust.vx
    )


def test_thrust_direction_is_normalized():
    """Scaling the thrust direction should not change its direction."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    state = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=500.0,
    )

    unit = rk4_step_thrust(
        state,
        dt=1.0,
        thrust_model=model,
        thrust_direction=(1.0, 0.0, 0.0),
    )

    scaled = rk4_step_thrust(
        state,
        dt=1.0,
        thrust_model=model,
        thrust_direction=(10.0, 0.0, 0.0),
    )

    assert scaled.vx == pytest.approx(
        unit.vx
    )
    assert scaled.vy == pytest.approx(
        unit.vy
    )
    assert scaled.vz == pytest.approx(
        unit.vz
    )


def test_thrust_can_act_in_z_direction():
    """A z-directed burn should produce out-of-plane velocity."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    state = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=500.0,
    )

    result = rk4_step_thrust(
        state,
        dt=10.0,
        thrust_model=model,
        thrust_direction=(0.0, 0.0, 1.0),
    )

    assert result.vz > state.vz


def test_gravity_is_included():
    """Gravity should accelerate the spacecraft toward Earth."""

    model = ThrustModel(
        thrust=0.0,
        specific_impulse=300.0,
    )

    state = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=500.0,
    )

    result = rk4_step_thrust(
        state,
        dt=1.0,
        thrust_model=model,
        thrust_direction=(1.0, 0.0, 0.0),
    )

    expected_acceleration = (
        -EARTH_MU /
        (7_000_000.0 ** 2)
    )

    assert result.vx == pytest.approx(
        expected_acceleration,
        rel=1e-3,
    )


def test_negative_timestep_is_rejected():
    """A non-positive timestep should be rejected."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    state = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=500.0,
    )

    with pytest.raises(ValueError):
        rk4_step_thrust(
            state,
            dt=0.0,
            thrust_model=model,
            thrust_direction=(1.0, 0.0, 0.0),
        )


def test_zero_thrust_direction_is_rejected():
    """The thrust direction cannot be the zero vector."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    state = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=500.0,
    )

    with pytest.raises(ValueError):
        rk4_step_thrust(
            state,
            dt=1.0,
            thrust_model=model,
            thrust_direction=(0.0, 0.0, 0.0),
        )


def test_non_positive_mass_is_rejected():
    """A spacecraft cannot propagate with non-positive mass."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    state = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=0.0,
    )

    with pytest.raises(ValueError):
        rk4_step_thrust(
            state,
            dt=1.0,
            thrust_model=model,
            thrust_direction=(1.0, 0.0, 0.0),
        )
