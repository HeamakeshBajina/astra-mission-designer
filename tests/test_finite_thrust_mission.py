"""Tests for ASTRA's integrated finite-thrust mission API."""

import pytest

from astra.physics.burn_vector import BurnVector
from astra.physics.thrust import ThrustModel
from astra.simulation.finite_burn import FiniteBurn
from astra.simulation.propagator_3d_thrust import State3DThrust
from astra.simulation.propagator_3d_thrust_j2 import State3DThrustJ2
from astra.mission.finite_thrust_mission import (
    FiniteThrustMission,
    MissionResult,
    run_finite_thrust_mission,
)


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


def make_thrust() -> ThrustModel:
    return ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )


def make_burn() -> FiniteBurn:
    return FiniteBurn(
        thrust_model=make_thrust(),
        duration=10.0,
        dry_mass=450.0,
    )


def make_mission(
    include_j2: bool = False,
) -> FiniteThrustMission:
    return FiniteThrustMission(
        initial_state=make_state(),
        thrust_model=make_thrust(),
        burn=make_burn(),
        burn_direction=BurnVector(1.0, 0.0, 0.0),
        timestep=1.0,
        include_j2=include_j2,
    )


def test_mission_configuration_is_valid():
    mission = make_mission()

    assert mission.timestep == 1.0
    assert mission.include_j2 is False


def test_mission_runs():
    result = run_finite_thrust_mission(
        make_mission()
    )

    assert isinstance(result, MissionResult)


def test_mission_duration_is_preserved():
    result = run_finite_thrust_mission(
        make_mission()
    )

    assert result.duration == pytest.approx(10.0)


def test_mission_consumes_propellant():
    result = run_finite_thrust_mission(
        make_mission()
    )

    assert result.propellant_consumed > 0.0
    assert result.mass_remaining < 500.0


def test_mission_respects_dry_mass():
    result = run_finite_thrust_mission(
        make_mission()
    )

    assert result.mass_remaining >= 450.0


def test_final_position_is_available():
    result = run_finite_thrust_mission(
        make_mission()
    )

    assert len(result.position) == 3


def test_final_velocity_is_available():
    result = run_finite_thrust_mission(
        make_mission()
    )

    assert len(result.velocity) == 3


def test_j2_mission_runs():
    result = run_finite_thrust_mission(
        make_mission(include_j2=True)
    )

    assert isinstance(
        result.final_state,
        State3DThrustJ2,
    )


def test_central_gravity_mission_uses_3d_state():
    result = run_finite_thrust_mission(
        make_mission()
    )

    assert isinstance(
        result.final_state,
        State3DThrust,
    )


def test_j2_flag_is_recorded():
    result = run_finite_thrust_mission(
        make_mission(include_j2=True)
    )

    assert result.include_j2 is True


def test_custom_timestep():
    mission = FiniteThrustMission(
        initial_state=make_state(),
        thrust_model=make_thrust(),
        burn=make_burn(),
        burn_direction=BurnVector(1.0, 1.0, 0.0),
        timestep=0.5,
    )

    result = run_finite_thrust_mission(mission)

    assert result.mass_remaining >= 450.0


def test_zero_direction_is_rejected():
    with pytest.raises(ValueError):
        FiniteThrustMission(
            initial_state=make_state(),
            thrust_model=make_thrust(),
            burn=make_burn(),
            burn_direction=BurnVector(0.0, 0.0, 0.0),
        )


def test_invalid_timestep_is_rejected():
    with pytest.raises(ValueError):
        FiniteThrustMission(
            initial_state=make_state(),
            thrust_model=make_thrust(),
            burn=make_burn(),
            burn_direction=BurnVector(1.0, 0.0, 0.0),
            timestep=0.0,
        )


def test_mismatched_thrust_models_are_rejected():
    different_thrust = ThrustModel(
        thrust=2000.0,
        specific_impulse=300.0,
    )

    with pytest.raises(ValueError):
        FiniteThrustMission(
            initial_state=make_state(),
            thrust_model=different_thrust,
            burn=make_burn(),
            burn_direction=BurnVector(1.0, 0.0, 0.0),
        )


def test_insufficient_propellant_is_rejected():
    short_state = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=500_000.0,
        vx=0.0,
        vy=7_200.0,
        vz=500.0,
        mass=450.1,
    )

    long_burn = FiniteBurn(
        thrust_model=make_thrust(),
        duration=2.0,
        dry_mass=450.0,
    )

    with pytest.raises(ValueError):
        FiniteThrustMission(
            initial_state=short_state,
            thrust_model=make_thrust(),
            burn=long_burn,
            burn_direction=BurnVector(1.0, 0.0, 0.0),
        )


def test_burn_direction_is_normalized():
    mission = FiniteThrustMission(
        initial_state=make_state(),
        thrust_model=make_thrust(),
        burn=make_burn(),
        burn_direction=BurnVector(10.0, 0.0, 0.0),
    )

    result = run_finite_thrust_mission(mission)

    assert result.mass_remaining >= 450.0


def test_j2_and_central_missions_have_same_mass_change():
    central = run_finite_thrust_mission(
        make_mission(include_j2=False)
    )
    j2 = run_finite_thrust_mission(
        make_mission(include_j2=True)
    )

    assert j2.mass_remaining == pytest.approx(
        central.mass_remaining
    )


def test_result_position_is_final_position():
    result = run_finite_thrust_mission(
        make_mission()
    )

    assert result.position[0] == pytest.approx(
        result.final_state.x
    )


def test_result_velocity_is_final_velocity():
    result = run_finite_thrust_mission(
        make_mission()
    )

    assert result.velocity[1] == pytest.approx(
        result.final_state.vy
    )


def test_non_divisible_duration_is_supported():
    burn = FiniteBurn(
        thrust_model=make_thrust(),
        duration=10.5,
        dry_mass=450.0,
    )

    mission = FiniteThrustMission(
        initial_state=make_state(),
        thrust_model=make_thrust(),
        burn=burn,
        burn_direction=BurnVector(0.0, 0.0, 1.0),
        timestep=2.0,
    )

    result = run_finite_thrust_mission(mission)

    expected_mass = (
        500.0
        - make_thrust().mass_flow_rate * 10.5
    )

    assert result.mass_remaining == pytest.approx(
        expected_mass
    )


def test_j2_mission_uses_j2_state_model():
    """The J2 mission path must return the dedicated J2 state."""
    result = run_finite_thrust_mission(
        make_mission(include_j2=True)
    )

    assert isinstance(
        result.final_state,
        State3DThrustJ2,
    )

    assert result.include_j2 is True


def test_mission_result_duration_matches_burn():
    mission = make_mission()

    result = run_finite_thrust_mission(mission)

    assert result.duration == mission.burn.duration
