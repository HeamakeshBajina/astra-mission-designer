"""Tests for ASTRA mission constraints and failure detection."""

import math

import pytest

from astra.mission.mission_constraints import (
    ConstraintType,
    MissionConstraints,
    MissionStatus,
    check_state_constraints,
    validate_final_state,
    validate_mission,
)
from astra.physics.constants import EARTH_RADIUS


LEO_RADIUS = EARTH_RADIUS + 400_000.0


def state(
    time: float = 0.0,
    radius: float = LEO_RADIUS,
    velocity: float = 7_700.0,
    mass: float = 1_000.0,
):
    return (
        time,
        (radius, 0.0, 0.0),
        (0.0, velocity, 0.0),
        mass,
    )


def test_default_constraints_are_valid():
    constraints = MissionConstraints()

    assert constraints.minimum_altitude == 0.0
    assert constraints.maximum_altitude is None
    assert constraints.minimum_mass == 0.0


def test_negative_minimum_altitude_rejected():
    with pytest.raises(ValueError):
        MissionConstraints(minimum_altitude=-1.0)


def test_invalid_altitude_range_rejected():
    with pytest.raises(ValueError):
        MissionConstraints(
            minimum_altitude=500_000.0,
            maximum_altitude=400_000.0,
        )


def test_negative_velocity_limit_rejected():
    with pytest.raises(ValueError):
        MissionConstraints(minimum_velocity=-1.0)

    with pytest.raises(ValueError):
        MissionConstraints(maximum_velocity=-1.0)


def test_invalid_velocity_range_rejected():
    with pytest.raises(ValueError):
        MissionConstraints(
            minimum_velocity=8_000.0,
            maximum_velocity=7_000.0,
        )


def test_negative_mass_limit_rejected():
    with pytest.raises(ValueError):
        MissionConstraints(minimum_mass=-1.0)


def test_invalid_duration_rejected():
    with pytest.raises(ValueError):
        MissionConstraints(maximum_duration=0.0)


def test_nominal_state_passes():
    result = check_state_constraints(
        position=(LEO_RADIUS, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        time=10.0,
        constraints=MissionConstraints(
            minimum_altitude=200_000.0,
            maximum_altitude=500_000.0,
            minimum_velocity=7_000.0,
            maximum_velocity=8_000.0,
            minimum_mass=900.0,
            maximum_duration=100.0,
        ),
    )

    assert result.valid
    assert result.violations == ()


def test_minimum_altitude_violation():
    result = check_state_constraints(
        position=(EARTH_RADIUS + 100_000.0, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        time=5.0,
        constraints=MissionConstraints(
            minimum_altitude=200_000.0
        ),
    )

    assert not result.valid
    assert result.violations[0].constraint_type == ConstraintType.ALTITUDE


def test_maximum_altitude_violation():
    result = check_state_constraints(
        position=(EARTH_RADIUS + 800_000.0, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        time=5.0,
        constraints=MissionConstraints(
            maximum_altitude=500_000.0
        ),
    )

    assert not result.valid
    assert result.violations[0].constraint_type == ConstraintType.ALTITUDE


def test_minimum_velocity_violation():
    result = check_state_constraints(
        position=(LEO_RADIUS, 0.0, 0.0),
        velocity=(0.0, 6_000.0, 0.0),
        mass=1_000.0,
        time=5.0,
        constraints=MissionConstraints(
            minimum_velocity=7_000.0
        ),
    )

    assert not result.valid
    assert result.violations[0].constraint_type == ConstraintType.VELOCITY


def test_maximum_velocity_violation():
    result = check_state_constraints(
        position=(LEO_RADIUS, 0.0, 0.0),
        velocity=(0.0, 9_000.0, 0.0),
        mass=1_000.0,
        time=5.0,
        constraints=MissionConstraints(
            maximum_velocity=8_000.0
        ),
    )

    assert not result.valid
    assert result.violations[0].constraint_type == ConstraintType.VELOCITY


def test_minimum_mass_violation():
    result = check_state_constraints(
        position=(LEO_RADIUS, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=800.0,
        time=5.0,
        constraints=MissionConstraints(
            minimum_mass=900.0
        ),
    )

    assert not result.valid
    assert result.violations[0].constraint_type == ConstraintType.DRY_MASS


def test_earth_impact_is_detected():
    result = check_state_constraints(
        position=(EARTH_RADIUS, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        time=5.0,
        constraints=MissionConstraints(),
    )

    assert not result.valid
    assert any(
        violation.constraint_type == ConstraintType.EARTH_IMPACT
        for violation in result.violations
    )


def test_below_earth_surface_is_detected():
    result = check_state_constraints(
        position=(EARTH_RADIUS - 1.0, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        time=5.0,
        constraints=MissionConstraints(),
    )

    assert not result.valid
    assert any(
        violation.constraint_type == ConstraintType.EARTH_IMPACT
        for violation in result.violations
    )


def test_duration_violation():
    result = check_state_constraints(
        position=(LEO_RADIUS, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        time=101.0,
        constraints=MissionConstraints(
            maximum_duration=100.0
        ),
    )

    assert not result.valid
    assert result.violations[0].constraint_type == ConstraintType.DURATION


def test_multiple_violations_are_reported():
    result = check_state_constraints(
        position=(EARTH_RADIUS + 100_000.0, 0.0, 0.0),
        velocity=(0.0, 9_000.0, 0.0),
        mass=500.0,
        time=200.0,
        constraints=MissionConstraints(
            minimum_altitude=200_000.0,
            maximum_velocity=8_000.0,
            minimum_mass=900.0,
            maximum_duration=100.0,
        ),
    )

    assert not result.valid
    assert len(result.violations) == 4


def test_invalid_position_length_rejected():
    with pytest.raises(ValueError):
        check_state_constraints(
            position=(LEO_RADIUS, 0.0),
            velocity=(0.0, 7_700.0, 0.0),
            mass=1_000.0,
            time=0.0,
            constraints=MissionConstraints(),
        )


def test_invalid_velocity_length_rejected():
    with pytest.raises(ValueError):
        check_state_constraints(
            position=(LEO_RADIUS, 0.0, 0.0),
            velocity=(0.0, 7_700.0),
            mass=1_000.0,
            time=0.0,
            constraints=MissionConstraints(),
        )


def test_nonfinite_position_rejected():
    with pytest.raises(ValueError):
        check_state_constraints(
            position=(math.inf, 0.0, 0.0),
            velocity=(0.0, 7_700.0, 0.0),
            mass=1_000.0,
            time=0.0,
            constraints=MissionConstraints(),
        )


def test_invalid_mass_rejected():
    with pytest.raises(ValueError):
        check_state_constraints(
            position=(LEO_RADIUS, 0.0, 0.0),
            velocity=(0.0, 7_700.0, 0.0),
            mass=0.0,
            time=0.0,
            constraints=MissionConstraints(),
        )


def test_invalid_time_rejected():
    with pytest.raises(ValueError):
        check_state_constraints(
            position=(LEO_RADIUS, 0.0, 0.0),
            velocity=(0.0, 7_700.0, 0.0),
            mass=1_000.0,
            time=-1.0,
            constraints=MissionConstraints(),
        )


def test_mission_success():
    result = validate_mission(
        [
            state(time=0.0),
            state(time=10.0),
            state(time=20.0),
        ],
        MissionConstraints(
            minimum_altitude=200_000.0,
            maximum_altitude=500_000.0,
            minimum_velocity=7_000.0,
            maximum_velocity=8_000.0,
            minimum_mass=900.0,
            maximum_duration=100.0,
        ),
    )

    assert result.status == MissionStatus.SUCCESS
    assert result.valid
    assert result.checked_points == 3
    assert result.failure_count == 0
    assert result.first_failure is None


def test_mission_failure_is_detected():
    result = validate_mission(
        [
            state(time=0.0),
            state(
                time=10.0,
                radius=EARTH_RADIUS + 100_000.0,
            ),
        ],
        MissionConstraints(
            minimum_altitude=200_000.0
        ),
    )

    assert result.status == MissionStatus.FAILURE
    assert not result.valid
    assert result.failure_count >= 1
    assert result.first_failure is not None


def test_mission_times_must_be_ordered():
    with pytest.raises(ValueError):
        validate_mission(
            [
                state(time=10.0),
                state(time=5.0),
            ],
            MissionConstraints(),
        )


def test_empty_mission_is_successful():
    result = validate_mission(
        [],
        MissionConstraints(),
    )

    assert result.status == MissionStatus.SUCCESS
    assert result.checked_points == 0
    assert result.final_time == 0.0


def test_final_state_validation_success():
    result = validate_final_state(
        position=(LEO_RADIUS, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        time=50.0,
        constraints=MissionConstraints(
            minimum_altitude=200_000.0
        ),
    )

    assert result.status == MissionStatus.SUCCESS
    assert result.valid


def test_final_state_validation_failure():
    result = validate_final_state(
        position=(EARTH_RADIUS + 100_000.0, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        time=50.0,
        constraints=MissionConstraints(
            minimum_altitude=200_000.0
        ),
    )

    assert result.status == MissionStatus.FAILURE
    assert not result.valid


def test_violation_contains_measurement_and_limit():
    result = check_state_constraints(
        position=(EARTH_RADIUS + 100_000.0, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        time=25.0,
        constraints=MissionConstraints(
            minimum_altitude=200_000.0
        ),
    )

    violation = result.violations[0]

    assert violation.time == 25.0
    assert violation.value == pytest.approx(100_000.0)
    assert violation.limit == 200_000.0


def test_violation_order_follows_detection_order():
    result = check_state_constraints(
        position=(EARTH_RADIUS + 100_000.0, 0.0, 0.0),
        velocity=(0.0, 9_000.0, 0.0),
        mass=500.0,
        time=25.0,
        constraints=MissionConstraints(
            minimum_altitude=200_000.0,
            maximum_velocity=8_000.0,
            minimum_mass=900.0,
        ),
    )

    assert result.violations[0].constraint_type == ConstraintType.ALTITUDE
    assert result.violations[1].constraint_type == ConstraintType.VELOCITY
    assert result.violations[2].constraint_type == ConstraintType.DRY_MASS


def test_zero_position_vector_is_detected_as_earth_impact():
    result = check_state_constraints(
        position=(0.0, 0.0, 0.0),
        velocity=(0.0, 0.0, 0.0),
        mass=1_000.0,
        time=0.0,
        constraints=MissionConstraints(),
    )

    assert not result.valid
    assert any(
        violation.constraint_type == ConstraintType.EARTH_IMPACT
        for violation in result.violations
    )
