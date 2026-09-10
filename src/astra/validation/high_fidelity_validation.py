"""High-fidelity validation utilities for ASTRA."""

from dataclasses import dataclass
import math
from collections.abc import Mapping, Sequence

from astra.physics.constants import EARTH_MU
from astra.physics.orbital import circular_orbital_velocity


@dataclass(frozen=True)
class ValidationMetric:
    """Validation result for one numerical quantity."""

    name: str
    expected: float
    actual: float
    absolute_error: float
    relative_error: float
    tolerance: float
    passed: bool


@dataclass(frozen=True)
class ScenarioValidationResult:
    """Validation result for an entire reference scenario."""

    name: str
    passed: bool
    metrics: tuple[ValidationMetric, ...]

    @property
    def failed_metrics(self) -> tuple[ValidationMetric, ...]:
        """Return metrics that failed validation."""
        return tuple(
            metric
            for metric in self.metrics
            if not metric.passed
        )

    @property
    def maximum_absolute_error(self) -> float:
        """Return the largest absolute error."""
        if not self.metrics:
            return 0.0
        return max(
            metric.absolute_error
            for metric in self.metrics
        )

    @property
    def maximum_relative_error(self) -> float:
        """Return the largest relative error."""
        if not self.metrics:
            return 0.0
        return max(
            metric.relative_error
            for metric in self.metrics
        )


@dataclass(frozen=True)
class ValidationReport:
    """Aggregate validation report."""

    passed: bool
    scenarios: tuple[ScenarioValidationResult, ...]

    @property
    def scenario_count(self) -> int:
        """Return the number of scenarios."""
        return len(self.scenarios)

    @property
    def passed_scenarios(self) -> int:
        """Return the number of passing scenarios."""
        return sum(
            scenario.passed
            for scenario in self.scenarios
        )

    @property
    def failed_scenarios(self) -> int:
        """Return the number of failing scenarios."""
        return sum(
            not scenario.passed
            for scenario in self.scenarios
        )

    @property
    def metric_count(self) -> int:
        """Return the total number of metrics."""
        return sum(
            len(scenario.metrics)
            for scenario in self.scenarios
        )


def _relative_error(
    expected: float,
    actual: float,
) -> float:
    """Calculate a stable relative error."""

    denominator = max(abs(expected), 1e-30)

    return abs(actual - expected) / denominator


def compare_value(
    name: str,
    expected: float,
    actual: float,
    tolerance: float,
) -> ValidationMetric:
    """Compare one numerical value against a reference."""

    if not math.isfinite(expected):
        raise ValueError(
            "Expected value must be finite."
        )

    if not math.isfinite(actual):
        raise ValueError(
            "Actual value must be finite."
        )

    if tolerance < 0:
        raise ValueError(
            "Tolerance cannot be negative."
        )

    absolute_error = abs(actual - expected)
    relative_error = _relative_error(
        expected=expected,
        actual=actual,
    )

    passed = (
        absolute_error <= tolerance
        or relative_error <= tolerance
    )

    return ValidationMetric(
        name=name,
        expected=expected,
        actual=actual,
        absolute_error=absolute_error,
        relative_error=relative_error,
        tolerance=tolerance,
        passed=passed,
    )


def validate_reference_scenario(
    name: str,
    expected_values: Mapping[str, float],
    actual_values: Mapping[str, float],
    tolerances: Mapping[str, float],
) -> ScenarioValidationResult:
    """Validate calculated values against reference values."""

    expected_keys = set(expected_values)
    actual_keys = set(actual_values)
    tolerance_keys = set(tolerances)

    if expected_keys != actual_keys:
        raise ValueError(
            "Expected and actual metric names must match."
        )

    if expected_keys != tolerance_keys:
        raise ValueError(
            "Every metric must have a corresponding tolerance."
        )

    metrics: list[ValidationMetric] = []

    for metric_name in expected_values:
        metrics.append(
            compare_value(
                name=metric_name,
                expected=expected_values[metric_name],
                actual=actual_values[metric_name],
                tolerance=tolerances[metric_name],
            )
        )

    return ScenarioValidationResult(
        name=name,
        passed=all(
            metric.passed
            for metric in metrics
        ),
        metrics=tuple(metrics),
    )


def validate_circular_orbit(
    radius: float,
    actual_velocity: float,
    tolerance: float = 1e-9,
) -> ScenarioValidationResult:
    """Validate circular orbital velocity independently."""

    if radius <= 0:
        raise ValueError(
            "Radius must be greater than zero."
        )

    expected_velocity = circular_orbital_velocity(
        radius
    )

    return validate_reference_scenario(
        name="Independent Circular Orbit Velocity",
        expected_values={
            "velocity": expected_velocity,
        },
        actual_values={
            "velocity": actual_velocity,
        },
        tolerances={
            "velocity": tolerance,
        },
    )


def specific_orbital_energy(
    radius: float,
    velocity: float,
) -> float:
    """Return specific orbital energy for a state."""

    if radius <= 0:
        raise ValueError(
            "Radius must be greater than zero."
        )

    return (
        velocity**2 / 2.0
        - EARTH_MU / radius
    )


def validate_circular_orbit_energy(
    radius: float,
    velocity: float,
    tolerance: float = 1e-6,
) -> ScenarioValidationResult:
    """Validate that a circular orbit has the expected energy."""

    if radius <= 0:
        raise ValueError(
            "Radius must be greater than zero."
        )

    if not math.isfinite(velocity):
        raise ValueError(
            "Velocity must be finite."
        )

    expected_energy = (
        -EARTH_MU / (2.0 * radius)
    )

    actual_energy = specific_orbital_energy(
        radius=radius,
        velocity=velocity,
    )

    return validate_reference_scenario(
        name="Circular Orbit Specific Energy",
        expected_values={
            "specific_energy": expected_energy,
        },
        actual_values={
            "specific_energy": actual_energy,
        },
        tolerances={
            "specific_energy": tolerance,
        },
    )


def validate_trajectory(
    expected_positions: Sequence[
        tuple[float, float, float]
    ],
    actual_positions: Sequence[
        tuple[float, float, float]
    ],
    position_tolerance: float,
) -> ScenarioValidationResult:
    """Validate a simulated position history."""

    if position_tolerance < 0:
        raise ValueError(
            "Position tolerance cannot be negative."
        )

    if len(expected_positions) != len(actual_positions):
        raise ValueError(
            "Expected and actual trajectories must have "
            "the same number of points."
        )

    metrics: list[ValidationMetric] = []

    for index, (
        expected,
        actual,
    ) in enumerate(
        zip(
            expected_positions,
            actual_positions,
        )
    ):
        if len(expected) != 3 or len(actual) != 3:
            raise ValueError(
                "Trajectory positions must be 3D vectors."
            )

        expected_norm = math.sqrt(
            sum(component**2 for component in expected)
        )

        error = math.sqrt(
            sum(
                (actual[i] - expected[i]) ** 2
                for i in range(3)
            )
        )

        relative_error = (
            error / max(expected_norm, 1e-30)
        )

        metrics.append(
            ValidationMetric(
                name=f"position[{index}]",
                expected=expected_norm,
                actual=math.sqrt(
                    sum(
                        component**2
                        for component in actual
                    )
                ),
                absolute_error=error,
                relative_error=relative_error,
                tolerance=position_tolerance,
                passed=error <= position_tolerance,
            )
        )

    return ScenarioValidationResult(
        name="Trajectory Position History",
        passed=all(
            metric.passed
            for metric in metrics
        ),
        metrics=tuple(metrics),
    )


def validate_convergence(
    coarse_error: float,
    medium_error: float,
    fine_error: float,
    tolerance: float,
    expected_order: float = 4.0,
) -> ScenarioValidationResult:
    """Validate numerical convergence toward a finer solution."""

    if coarse_error < 0:
        raise ValueError(
            "Coarse error cannot be negative."
        )

    if medium_error < 0:
        raise ValueError(
            "Medium error cannot be negative."
        )

    if fine_error < 0:
        raise ValueError(
            "Fine error cannot be negative."
        )

    if tolerance < 0:
        raise ValueError(
            "Tolerance cannot be negative."
        )

    if expected_order <= 0:
        raise ValueError(
            "Expected convergence order must be positive."
        )

    coarse_to_medium = (
        math.inf
        if medium_error == 0.0
        else coarse_error / medium_error
    )

    medium_to_fine = (
        math.inf
        if fine_error == 0.0
        else medium_error / fine_error
    )

    expected_ratio = 2.0 ** expected_order

    metrics = (
        compare_value(
            name="medium_error",
            expected=0.0,
            actual=medium_error,
            tolerance=tolerance,
        ),
        compare_value(
            name="coarse_to_medium_ratio",
            expected=expected_ratio,
            actual=coarse_to_medium,
            tolerance=expected_ratio,
        ),
        compare_value(
            name="medium_to_fine_ratio",
            expected=expected_ratio,
            actual=medium_to_fine,
            tolerance=expected_ratio,
        ),
    )

    return ScenarioValidationResult(
        name="Numerical Convergence",
        passed=(
            medium_error <= tolerance
            and coarse_error >= medium_error
            and medium_error >= fine_error
        ),
        metrics=metrics,
    )


def build_validation_report(
    scenarios: Sequence[
        ScenarioValidationResult
    ],
) -> ValidationReport:
    """Build an aggregate validation report."""

    scenario_tuple = tuple(scenarios)

    return ValidationReport(
        passed=all(
            scenario.passed
            for scenario in scenario_tuple
        ),
        scenarios=scenario_tuple,
    )



