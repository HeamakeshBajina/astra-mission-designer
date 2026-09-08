"""Tests for ASTRA's combined J2 and finite-thrust propagator."""

import pytest

from astra.physics.burn_vector import BurnVector
from astra.physics.j2 import j2_acceleration
from astra.physics.thrust import ThrustModel
from astra.simulation.finite_burn import FiniteBurn
from astra.simulation.propagator_3d_thrust_j2 import (
    State3DThrustJ2,
    rk4_step_thrust_j2,
)


def make_state() -> State3DThrustJ2:
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


def test_j2_acceleration_is_nonzero():
    acceleration = j2_acceleration(
        x=7_000_000.0,
        y=0.0,
        z=500_000.0,
    )

    assert any(
        component != 0.0
        for component in acceleration
    )


def test_j2_acceleration_has_three_components():
    acceleration = j2_acceleration(
        x=7_000_000.0,
        y=100_000.0,
        z=500_000.0,
    )

    assert len(acceleration) == 3


def test_combined_state_is_valid():
    result = rk4_step_thrust_j2(
        state=make_state(),
        dt=1.0,
        thrust_model=make_thrust(),
        thrust_direction=BurnVector(1.0, 0.0, 0.0),
        dry_mass=450.0,
    )

    assert isinstance(result, State3DThrustJ2)


def test_mass_decreases_during_thrust():
    initial = make_state()

    result = rk4_step_thrust_j2(
        state=initial,
        dt=1.0,
        thrust_model=make_thrust(),
        thrust_direction=(1.0, 0.0, 0.0),
        dry_mass=450.0,
    )

    assert result.mass < initial.mass


def test_mass_change_matches_mass_flow():
    initial = make_state()
    thrust = make_thrust()
    dt = 2.0

    result = rk4_step_thrust_j2(
        state=initial,
        dt=dt,
        thrust_model=thrust,
        thrust_direction=(1.0, 0.0, 0.0),
        dry_mass=450.0,
    )

    expected_mass = initial.mass - thrust.mass_flow_rate * dt

    assert result.mass == pytest.approx(expected_mass)


def test_j2_acceleration_is_genuinely_nonzero():
    """The J2 acceleration must not collapse to an exact zero vector."""
    acceleration = j2_acceleration(
        x=7_000_000.0,
        y=100_000.0,
        z=500_000.0,
    )

    assert acceleration != (0.0, 0.0, 0.0)


def test_combined_propagator_uses_j2():
    initial = make_state()

    result = rk4_step_thrust_j2(
        state=initial,
        dt=100.0,
        thrust_model=ThrustModel(
            thrust=0.0,
            specific_impulse=300.0,
        ),
        thrust_direction=(1.0, 0.0, 0.0),
        dry_mass=450.0,
    )

    assert result.x != initial.x
    assert result.y != initial.y
    assert result.z != initial.z


def test_thrust_changes_velocity():
    initial = make_state()

    result = rk4_step_thrust_j2(
        state=initial,
        dt=10.0,
        thrust_model=make_thrust(),
        thrust_direction=(0.0, 0.0, 1.0),
        dry_mass=450.0,
    )

    assert result.vz != initial.vz


def test_three_dimensional_thrust_works():
    initial = make_state()

    result = rk4_step_thrust_j2(
        state=initial,
        dt=1.0,
        thrust_model=make_thrust(),
        thrust_direction=BurnVector(1.0, 2.0, 3.0),
        dry_mass=450.0,
    )

    assert result.vz != initial.vz


def test_zero_direction_is_rejected():
    with pytest.raises(ValueError):
        rk4_step_thrust_j2(
            state=make_state(),
            dt=1.0,
            thrust_model=make_thrust(),
            thrust_direction=(0.0, 0.0, 0.0),
            dry_mass=450.0,
        )


def test_invalid_timestep_is_rejected():
    with pytest.raises(ValueError):
        rk4_step_thrust_j2(
            state=make_state(),
            dt=0.0,
            thrust_model=make_thrust(),
            thrust_direction=(1.0, 0.0, 0.0),
            dry_mass=450.0,
        )


def test_invalid_dry_mass_is_rejected():
    with pytest.raises(ValueError):
        rk4_step_thrust_j2(
            state=make_state(),
            dt=1.0,
            thrust_model=make_thrust(),
            thrust_direction=(1.0, 0.0, 0.0),
            dry_mass=0.0,
        )


def test_insufficient_propellant_is_rejected():
    state = State3DThrustJ2(
        x=7_000_000.0,
        y=0.0,
        z=500_000.0,
        vx=0.0,
        vy=7_200.0,
        vz=500.0,
        mass=450.5,
    )

    with pytest.raises(ValueError):
        rk4_step_thrust_j2(
            state=state,
            dt=2.0,
            thrust_model=make_thrust(),
            thrust_direction=(1.0, 0.0, 0.0),
            dry_mass=450.0,
        )


def test_position_changes():
    initial = make_state()

    result = rk4_step_thrust_j2(
        state=initial,
        dt=1.0,
        thrust_model=make_thrust(),
        thrust_direction=(1.0, 0.0, 0.0),
        dry_mass=450.0,
    )

    assert result.x != pytest.approx(
        initial.x,
        abs=1e-9,
        rel=0.0,
    )

    assert result.y != pytest.approx(
        initial.y,
        abs=1e-9,
        rel=0.0,
    )


def test_z_position_changes_with_out_of_plane_thrust():
    initial = make_state()

    result = rk4_step_thrust_j2(
        state=initial,
        dt=10.0,
        thrust_model=make_thrust(),
        thrust_direction=(0.0, 0.0, 1.0),
        dry_mass=450.0,
    )

    assert result.z != pytest.approx(
        initial.z,
        abs=1e-9,
        rel=0.0,
    )


def test_finite_burn_model_is_compatible():
    burn = FiniteBurn(
        thrust_model=make_thrust(),
        duration=10.0,
        dry_mass=450.0,
    )

    initial = make_state()

    assert burn.can_complete(initial.mass)

    result = rk4_step_thrust_j2(
        state=initial,
        dt=1.0,
        thrust_model=burn.thrust_model,
        thrust_direction=(1.0, 0.0, 0.0),
        dry_mass=burn.dry_mass,
    )

    assert result.mass < initial.mass
