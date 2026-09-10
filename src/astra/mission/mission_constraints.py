"""Mission constraints and failure detection for ASTRA."""

from dataclasses import dataclass
from enum import Enum
import math
from collections.abc import Iterable


class MissionStatus(str, Enum):
    """Overall mission validity status."""

    NOMINAL = "nominal"
    SUCCESS = "success"
    FAILURE = "failure"


class ConstraintType(str, Enum):
    """Types of mission constraints."""

    ALTITUDE = "altitude"
    VELOCITY = "velocity"
    PROPELLANT = "propellant"
    DRY_MASS = "dry_mass"
    DURATION = "duration"
    EARTH_IMPACT = "earth_impact"


@dataclass(frozen=True)
class MissionConstraints:
    """Operational constraints applied to a spacecraft trajectory."""

    minimum_altitude: float = 0.0
    maximum_altitude: float | None = None
    minimum_velocity: float | None = None
    maximum_velocity: float | None = None
    minimum_mass: float = 0.0
    maximum_duration: float | None = None

    def __post_init__(self) -> None:
        if self.minimum_altitude < 0:
            raise ValueError(
                "Minimum altitude cannot be negative."
            )

        if (
            self.maximum_altitude is not None
            and self.maximum_altitude <= self.minimum_altitude
        ):
            raise ValueError(
                "Maximum altitude must be greater than minimum altitude."
            )

        if (
            self.minimum_velocity is not None
            and self.minimum_velocity < 0
        ):
            raise ValueError(
                "Minimum velocity cannot be negative."
            )

        if (
            self.maximum_velocity is not None
            and self.maximum_velocity < 0
        ):
            raise ValueError(
                "Maximum velocity cannot be negative."
            )

        if (
            self.minimum_velocity is not None
            and self.maximum_velocity is not None
            and self.maximum_velocity < self.minimum_velocity
        ):
            raise ValueError(
                "Maximum velocity must be greater than minimum velocity."
            )

        if self.minimum_mass < 0:
            raise ValueError(
                "Minimum mass cannot be negative."
            )

        if (
            self.maximum_duration is not None
            and self.maximum_duration <= 0
        ):
            raise ValueError(
                "Maximum duration must be greater than zero."
            )


@dataclass(frozen=True)
class ConstraintViolation:
    """A single detected mission constraint violation."""

    constraint_type: ConstraintType
    message: str
    time: float
    value: float
    limit: float


@dataclass(frozen=True)
class ConstraintCheck:
    """Result of evaluating one spacecraft state."""

    violations: tuple[ConstraintViolation, ...]

    @property
    def valid(self) -> bool:
        """Return True when no constraints are violated."""
        return len(self.violations) == 0


@dataclass(frozen=True)
class MissionValidation:
    """Complete mission constraint evaluation."""

    status: MissionStatus
    violations: tuple[ConstraintViolation, ...]
    checked_points: int
    final_time: float

    @property
    def valid(self) -> bool:
        """Return True when the mission has no violations."""
        return self.status != MissionStatus.FAILURE

    @property
    def failure_count(self) -> int:
        """Return the number of detected violations."""
        return len(self.violations)

    @property
    def first_failure(self) -> ConstraintViolation | None:
        """Return the earliest detected violation."""
        if not self.violations:
            return None
        return self.violations[0]


def _validate_state(
    position: tuple[float, float, float],
    velocity: tuple[float, float, float],
    mass: float,
    time: float,
) -> None:
    """Validate basic spacecraft state inputs."""

    if len(position) != 3:
        raise ValueError(
            "Position must contain exactly three components."
        )

    if len(velocity) != 3:
        raise ValueError(
            "Velocity must contain exactly three components."
        )

    if not all(math.isfinite(value) for value in position):
        raise ValueError(
            "Position must contain finite values."
        )

    if not all(math.isfinite(value) for value in velocity):
        raise ValueError(
            "Velocity must contain finite values."
        )

    if not math.isfinite(mass) or mass <= 0:
        raise ValueError(
            "Mass must be greater than zero and finite."
        )

    if not math.isfinite(time) or time < 0:
        raise ValueError(
            "Time must be finite and non-negative."
        )


def check_state_constraints(
    position: tuple[float, float, float],
    velocity: tuple[float, float, float],
    mass: float,
    time: float,
    constraints: MissionConstraints,
) -> ConstraintCheck:
    """Check one spacecraft state against mission constraints."""

    _validate_state(
        position=position,
        velocity=velocity,
        mass=mass,
        time=time,
    )

    radius = math.sqrt(
        position[0] ** 2
        + position[1] ** 2
        + position[2] ** 2
    )

    velocity_magnitude = math.sqrt(
        velocity[0] ** 2
        + velocity[1] ** 2
        + velocity[2] ** 2
    )

    from astra.physics.constants import EARTH_RADIUS

    altitude = radius - EARTH_RADIUS

    violations: list[ConstraintViolation] = []

    if altitude < constraints.minimum_altitude:
        violations.append(
            ConstraintViolation(
                constraint_type=ConstraintType.ALTITUDE,
                message=(
                    "Spacecraft altitude is below the "
                    "minimum permitted altitude."
                ),
                time=time,
                value=altitude,
                limit=constraints.minimum_altitude,
            )
        )

    if (
        constraints.maximum_altitude is not None
        and altitude > constraints.maximum_altitude
    ):
        violations.append(
            ConstraintViolation(
                constraint_type=ConstraintType.ALTITUDE,
                message=(
                    "Spacecraft altitude exceeds the "
                    "maximum permitted altitude."
                ),
                time=time,
                value=altitude,
                limit=constraints.maximum_altitude,
            )
        )

    if (
        constraints.minimum_velocity is not None
        and velocity_magnitude < constraints.minimum_velocity
    ):
        violations.append(
            ConstraintViolation(
                constraint_type=ConstraintType.VELOCITY,
                message=(
                    "Spacecraft velocity is below the "
                    "minimum permitted velocity."
                ),
                time=time,
                value=velocity_magnitude,
                limit=constraints.minimum_velocity,
            )
        )

    if (
        constraints.maximum_velocity is not None
        and velocity_magnitude > constraints.maximum_velocity
    ):
        violations.append(
            ConstraintViolation(
                constraint_type=ConstraintType.VELOCITY,
                message=(
                    "Spacecraft velocity exceeds the "
                    "maximum permitted velocity."
                ),
                time=time,
                value=velocity_magnitude,
                limit=constraints.maximum_velocity,
            )
        )

    if mass < constraints.minimum_mass:
        violations.append(
            ConstraintViolation(
                constraint_type=ConstraintType.DRY_MASS,
                message=(
                    "Spacecraft mass is below the "
                    "minimum permitted mass."
                ),
                time=time,
                value=mass,
                limit=constraints.minimum_mass,
            )
        )

    if altitude <= 0.0:
        violations.append(
            ConstraintViolation(
                constraint_type=ConstraintType.EARTH_IMPACT,
                message=(
                    "Spacecraft radius is at or below "
                    "Earth's surface."
                ),
                time=time,
                value=altitude,
                limit=0.0,
            )
        )

    if (
        constraints.maximum_duration is not None
        and time > constraints.maximum_duration
    ):
        violations.append(
            ConstraintViolation(
                constraint_type=ConstraintType.DURATION,
                message=(
                    "Mission elapsed time exceeds the "
                    "maximum permitted duration."
                ),
                time=time,
                value=time,
                limit=constraints.maximum_duration,
            )
        )

    return ConstraintCheck(
        violations=tuple(violations)
    )


def validate_mission(
    states: Iterable[
        tuple[
            float,
            tuple[float, float, float],
            tuple[float, float, float],
            float,
        ]
    ],
    constraints: MissionConstraints,
) -> MissionValidation:
    """Validate a sequence of time-tagged spacecraft states.

    Each state is:
        (time, position, velocity, mass)
    """

    violations: list[ConstraintViolation] = []
    checked_points = 0
    final_time = 0.0

    previous_time = -math.inf

    for time, position, velocity, mass in states:
        if time < previous_time:
            raise ValueError(
                "Mission state times must be non-decreasing."
            )

        check = check_state_constraints(
            position=position,
            velocity=velocity,
            mass=mass,
            time=time,
            constraints=constraints,
        )

        violations.extend(check.violations)

        checked_points += 1
        final_time = time
        previous_time = time

    status = (
        MissionStatus.FAILURE
        if violations
        else MissionStatus.SUCCESS
    )

    return MissionValidation(
        status=status,
        violations=tuple(violations),
        checked_points=checked_points,
        final_time=final_time,
    )


def validate_final_state(
    position: tuple[float, float, float],
    velocity: tuple[float, float, float],
    mass: float,
    time: float,
    constraints: MissionConstraints,
) -> MissionValidation:
    """Validate a single final spacecraft state."""

    check = check_state_constraints(
        position=position,
        velocity=velocity,
        mass=mass,
        time=time,
        constraints=constraints,
    )

    status = (
        MissionStatus.FAILURE
        if not check.valid
        else MissionStatus.SUCCESS
    )

    return MissionValidation(
        status=status,
        violations=check.violations,
        checked_points=1,
        final_time=time,
    )
