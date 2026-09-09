"""Mission-level validation utilities for ASTRA."""

from dataclasses import dataclass

from astra.mission.mission_replay import MissionReplay
from astra.simulation.trajectory_history import TrajectoryHistory


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating a completed spacecraft mission."""

    passed: bool
    time_error: float
    mass_error: float
    final_position_error: float
    final_velocity_error: float
    messages: tuple[str, ...]

    @property
    def failure_count(self) -> int:
        """Return the number of failed validation checks."""

        return sum(
            1
            for message in self.messages
            if message.startswith("FAIL:")
        )


def validate_trajectory_history(
    history: TrajectoryHistory,
    expected_duration: float | None = None,
    expected_final_mass: float | None = None,
    duration_tolerance: float = 1e-9,
    mass_tolerance: float = 1e-9,
) -> ValidationResult:
    """Validate fundamental properties of a trajectory history.

    Checks:
    - trajectory contains recorded points
    - mission time reaches the requested duration
    - final spacecraft mass matches an expected value

    Parameters
    ----------
    history:
        Completed ASTRA trajectory history.

    expected_duration:
        Optional expected final mission time.

    expected_final_mass:
        Optional expected final spacecraft mass.

    duration_tolerance:
        Maximum allowed time error in seconds.

    mass_tolerance:
        Maximum allowed mass error in kilograms.
    """

    if duration_tolerance <= 0:
        raise ValueError(
            "Duration tolerance must be greater than zero."
        )

    if mass_tolerance <= 0:
        raise ValueError(
            "Mass tolerance must be greater than zero."
        )

    if expected_duration is not None:
        if expected_duration < 0:
            raise ValueError(
                "Expected duration cannot be negative."
            )

    if expected_final_mass is not None:
        if expected_final_mass <= 0:
            raise ValueError(
                "Expected final mass must be greater than zero."
            )

    messages: list[str] = []

    time_error = 0.0
    mass_error = 0.0

    if history.point_count <= 0:
        messages.append(
            "FAIL: trajectory contains no recorded points."
        )
    else:
        messages.append(
            "PASS: trajectory contains recorded points."
        )

    if expected_duration is not None:
        time_error = abs(
            history.final_time - expected_duration
        )

        if time_error <= duration_tolerance:
            messages.append(
                "PASS: final mission time matches expectation."
            )
        else:
            messages.append(
                "FAIL: final mission time differs from expectation."
            )

    if expected_final_mass is not None:
        mass_error = abs(
            history.final_state.mass
            - expected_final_mass
        )

        if mass_error <= mass_tolerance:
            messages.append(
                "PASS: final spacecraft mass matches expectation."
            )
        else:
            messages.append(
                "FAIL: final spacecraft mass differs from expectation."
            )

    passed = not any(
        message.startswith("FAIL:")
        for message in messages
    )

    return ValidationResult(
        passed=passed,
        time_error=time_error,
        mass_error=mass_error,
        final_position_error=0.0,
        final_velocity_error=0.0,
        messages=tuple(messages),
    )


def validate_final_state(
    history: TrajectoryHistory,
    reference_position: tuple[float, float, float],
    reference_velocity: tuple[float, float, float],
    position_tolerance: float,
    velocity_tolerance: float,
) -> ValidationResult:
    """Validate the final spacecraft state against a reference state."""

    if position_tolerance <= 0:
        raise ValueError(
            "Position tolerance must be greater than zero."
        )

    if velocity_tolerance <= 0:
        raise ValueError(
            "Velocity tolerance must be greater than zero."
        )

    if len(reference_position) != 3:
        raise ValueError(
            "Reference position must contain three components."
        )

    if len(reference_velocity) != 3:
        raise ValueError(
            "Reference velocity must contain three components."
        )

    final_state = history.final_state

    final_position = (
        final_state.x,
        final_state.y,
        final_state.z,
    )

    final_velocity = (
        final_state.vx,
        final_state.vy,
        final_state.vz,
    )

    position_error = sum(
        (
            final_position[index]
            - reference_position[index]
        ) ** 2
        for index in range(3)
    ) ** 0.5

    velocity_error = sum(
        (
            final_velocity[index]
            - reference_velocity[index]
        ) ** 2
        for index in range(3)
    ) ** 0.5

    messages: list[str] = []

    if position_error <= position_tolerance:
        messages.append(
            "PASS: final position is within tolerance."
        )
    else:
        messages.append(
            "FAIL: final position exceeds tolerance."
        )

    if velocity_error <= velocity_tolerance:
        messages.append(
            "PASS: final velocity is within tolerance."
        )
    else:
        messages.append(
            "FAIL: final velocity exceeds tolerance."
        )

    passed = not any(
        message.startswith("FAIL:")
        for message in messages
    )

    return ValidationResult(
        passed=passed,
        time_error=0.0,
        mass_error=0.0,
        final_position_error=position_error,
        final_velocity_error=velocity_error,
        messages=tuple(messages),
    )


def validate_replay_consistency(
    history: TrajectoryHistory,
) -> ValidationResult:
    """Validate that mission replay reproduces the trajectory endpoints."""

    replay = MissionReplay(history)

    initial_position = history.positions[0]
    final_position = history.positions[-1]

    replay_initial_position = replay.position_at(
        history.times[0]
    )

    replay_final_position = replay.position_at(
        history.final_time
    )

    initial_error = sum(
        (
            replay_initial_position[index]
            - initial_position[index]
        ) ** 2
        for index in range(3)
    ) ** 0.5

    final_error = sum(
        (
            replay_final_position[index]
            - final_position[index]
        ) ** 2
        for index in range(3)
    ) ** 0.5

    passed = (
        initial_error == 0.0
        and final_error == 0.0
    )

    if passed:
        messages = (
            "PASS: replay reproduces the trajectory endpoints.",
        )
    else:
        messages = (
            "FAIL: replay does not reproduce the trajectory endpoints.",
        )

    return ValidationResult(
        passed=passed,
        time_error=0.0,
        mass_error=0.0,
        final_position_error=final_error,
        final_velocity_error=0.0,
        messages=messages,
    )
