"""Tests for ASTRA mission-level validation."""

import math

import pytest

from astra.mission.mission_validation import (
    ValidationResult,
    validate_final_state,
    validate_replay_consistency,
    validate_trajectory_history,
)
from astra.physics.burn_vector import BurnVector
from astra.physics.constants import EARTH_MU, EARTH_RADIUS
from astra.physics.thrust import ThrustModel
from astra.simulation.propagator_3d_thrust import State3DThrust
from astra.simulation.trajectory_history import simulate_trajectory


def circular_state(
    altitude: float = 400_000.0,
) -> State3DThrust:
    """Return a circular equatorial orbit state."""

    radius = EARTH_RADIUS + altitude
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
        mass=500.0,
    )


def make_history():
    """Create a deterministic zero-thrust trajectory."""

    return simulate_trajectory(
        initial_state=circular_state(),
        duration=10.0,
        timestep=1.0,
        thrust_model=ThrustModel(
            thrust=0.0,
            specific_impulse=300.0,
        ),
        thrust_direction=BurnVector(
            1.0,
            0.0,
            0.0,
        ),
    )


def test_validation_result_is_dataclass() -> None:
    """Validation should return the documented result type."""

    result = validate_trajectory_history(
        make_history(),
    )

    assert isinstance(
        result,
        ValidationResult,
    )


def test_trajectory_validation_passes_without_optional_checks() -> None:
    """A valid trajectory should pass fundamental validation."""

    result = validate_trajectory_history(
        make_history(),
    )

    assert result.passed is True
    assert result.failure_count == 0


def test_trajectory_validation_checks_duration() -> None:
    """Expected mission duration should be validated."""

    result = validate_trajectory_history(
        make_history(),
        expected_duration=10.0,
    )

    assert result.passed is True
    assert result.time_error == pytest.approx(0.0)


def test_trajectory_validation_detects_duration_error() -> None:
    """Incorrect expected duration should fail validation."""

    result = validate_trajectory_history(
        make_history(),
        expected_duration=11.0,
    )

    assert result.passed is False
    assert result.time_error == pytest.approx(1.0)
    assert result.failure_count == 1


def test_trajectory_validation_checks_final_mass() -> None:
    """Expected final mass should be validated."""

    result = validate_trajectory_history(
        make_history(),
        expected_final_mass=500.0,
    )

    assert result.passed is True
    assert result.mass_error == pytest.approx(0.0)


def test_trajectory_validation_detects_mass_error() -> None:
    """Incorrect expected mass should fail validation."""

    result = validate_trajectory_history(
        make_history(),
        expected_final_mass=499.0,
    )

    assert result.passed is False
    assert result.mass_error == pytest.approx(1.0)


def test_trajectory_validation_accepts_tolerance() -> None:
    """Small duration differences within tolerance should pass."""

    history = make_history()

    result = validate_trajectory_history(
        history,
        expected_duration=10.000001,
        duration_tolerance=1e-5,
    )

    assert result.passed is True


def test_trajectory_validation_rejects_invalid_duration_tolerance() -> None:
    """Duration tolerance must be positive."""

    with pytest.raises(
        ValueError,
        match="Duration tolerance",
    ):
        validate_trajectory_history(
            make_history(),
            duration_tolerance=0.0,
        )


def test_trajectory_validation_rejects_invalid_mass_tolerance() -> None:
    """Mass tolerance must be positive."""

    with pytest.raises(
        ValueError,
        match="Mass tolerance",
    ):
        validate_trajectory_history(
            make_history(),
            mass_tolerance=0.0,
        )


def test_expected_duration_cannot_be_negative() -> None:
    """Negative expected duration must be rejected."""

    with pytest.raises(
        ValueError,
        match="Expected duration",
    ):
        validate_trajectory_history(
            make_history(),
            expected_duration=-1.0,
        )


def test_expected_mass_must_be_positive() -> None:
    """Expected final mass must be positive."""

    with pytest.raises(
        ValueError,
        match="Expected final mass",
    ):
        validate_trajectory_history(
            make_history(),
            expected_final_mass=0.0,
        )


def test_final_state_validation_passes_exact_reference() -> None:
    """An exact final state should pass validation."""

    history = make_history()

    result = validate_final_state(
        history=history,
        reference_position=history.positions[-1],
        reference_velocity=history.velocities[-1],
        position_tolerance=1e-6,
        velocity_tolerance=1e-9,
    )

    assert result.passed is True
    assert result.final_position_error == pytest.approx(0.0)
    assert result.final_velocity_error == pytest.approx(0.0)


def test_final_state_validation_detects_position_error() -> None:
    """A displaced reference position should fail."""

    history = make_history()
    reference = history.positions[-1]

    result = validate_final_state(
        history=history,
        reference_position=(
            reference[0] + 100.0,
            reference[1],
            reference[2],
        ),
        reference_velocity=history.velocities[-1],
        position_tolerance=1.0,
        velocity_tolerance=1e-9,
    )

    assert result.passed is False
    assert result.final_position_error == pytest.approx(100.0)


def test_final_state_validation_detects_velocity_error() -> None:
    """A changed reference velocity should fail."""

    history = make_history()
    reference = history.velocities[-1]

    result = validate_final_state(
        history=history,
        reference_position=history.positions[-1],
        reference_velocity=(
            reference[0] + 1.0,
            reference[1],
            reference[2],
        ),
        position_tolerance=1e-6,
        velocity_tolerance=0.1,
    )

    assert result.passed is False
    assert result.final_velocity_error == pytest.approx(1.0)


def test_final_state_validation_rejects_invalid_position_tolerance() -> None:
    """Position tolerance must be positive."""

    history = make_history()

    with pytest.raises(
        ValueError,
        match="Position tolerance",
    ):
        validate_final_state(
            history,
            history.positions[-1],
            history.velocities[-1],
            0.0,
            1.0,
        )


def test_final_state_validation_rejects_invalid_velocity_tolerance() -> None:
    """Velocity tolerance must be positive."""

    history = make_history()

    with pytest.raises(
        ValueError,
        match="Velocity tolerance",
    ):
        validate_final_state(
            history,
            history.positions[-1],
            history.velocities[-1],
            1.0,
            0.0,
        )


def test_final_state_validation_requires_three_position_components() -> None:
    """Reference positions must be three-dimensional."""

    history = make_history()

    with pytest.raises(
        ValueError,
        match="three components",
    ):
        validate_final_state(
            history,
            (1.0, 2.0),
            history.velocities[-1],
            1.0,
            1.0,
        )


def test_final_state_validation_requires_three_velocity_components() -> None:
    """Reference velocities must be three-dimensional."""

    history = make_history()

    with pytest.raises(
        ValueError,
        match="three components",
    ):
        validate_final_state(
            history,
            history.positions[-1],
            (1.0, 2.0),
            1.0,
            1.0,
        )


def test_replay_consistency_passes() -> None:
    """Mission replay should reproduce trajectory endpoints."""

    result = validate_replay_consistency(
        make_history()
    )

    assert result.passed is True
    assert result.failure_count == 0
    assert result.final_position_error == pytest.approx(0.0)


def test_validation_messages_identify_pass_or_fail() -> None:
    """Validation results should expose human-readable messages."""

    result = validate_trajectory_history(
        make_history(),
        expected_duration=11.0,
    )

    assert any(
        message.startswith("FAIL:")
        for message in result.messages
    )
