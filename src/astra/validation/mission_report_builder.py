"""Build mission reports from ASTRA reference-scenario calculations."""

from __future__ import annotations

from collections.abc import Mapping
import math
from typing import Any

from astra.validation.high_fidelity_validation import (
    validate_reference_scenario,
)
from astra.validation.mission_report import (
    CheckStatus,
    MissionValidationReport,
    ValidationCheck,
)
from astra.validation.reference_scenarios import all_reference_scenarios


def build_reference_mission_report(
    *,
    mission_name: str,
    created_at: str,
    software_version: str,
    actual_values: Mapping[str, Mapping[str, float]],
    inputs: Mapping[str, Any] | None = None,
    assumptions: tuple[str, ...] = (
        "Reference scenarios use ASTRA's documented idealized models.",
        "A passing reference check does not establish flight readiness.",
    ),
    notes: tuple[str, ...] = (),
) -> MissionValidationReport:
    """Compare supplied calculated values with ASTRA reference scenarios.

    ``actual_values`` maps each exact reference scenario name to its
    calculated metric values. Missing scenarios or metrics are recorded
    as NOT RUN; they are never assumed to have passed.
    """
    reference_scenarios = all_reference_scenarios()
    known_names = {scenario.name for scenario in reference_scenarios}
    checks: list[ValidationCheck] = []

    for scenario in reference_scenarios:
        supplied = actual_values.get(scenario.name)

        if supplied is None:
            for metric_name in scenario.expected_values:
                checks.append(
                    ValidationCheck(
                        check_id=f"{scenario.name}:{metric_name}",
                        name=f"{scenario.name} — {metric_name}",
                        status=CheckStatus.NOT_RUN,
                        summary="No calculated value was supplied.",
                        details=(
                            "This metric has not been validated by "
                            "this report-building call."
                        ),
                        value=None,
                        threshold=scenario.tolerances[metric_name],
                    )
                )
            continue

        unexpected = set(supplied) - set(scenario.expected_values)
        if unexpected:
            raise ValueError(
                f"Unexpected metrics for {scenario.name}: "
                f"{sorted(unexpected)}"
            )

        available = {
            name: value
            for name, value in supplied.items()
            if name in scenario.expected_values
        }

        missing = set(scenario.expected_values) - set(available)

        for metric_name in sorted(missing):
            checks.append(
                ValidationCheck(
                    check_id=f"{scenario.name}:{metric_name}",
                    name=f"{scenario.name} — {metric_name}",
                    status=CheckStatus.NOT_RUN,
                    summary="No calculated value was supplied.",
                    threshold=scenario.tolerances[metric_name],
                )
            )

        if not available:
            continue

        for metric_name, value in available.items():
            if not math.isfinite(value):
                raise ValueError(
                    f"Calculated value for {scenario.name} / "
                    f"{metric_name} must be finite."
                )

        expected_available = {
            name: scenario.expected_values[name]
            for name in available
        }
        tolerances_available = {
            name: scenario.tolerances[name]
            for name in available
        }

        result = validate_reference_scenario(
            name=scenario.name,
            expected_values=expected_available,
            actual_values=available,
            tolerances=tolerances_available,
        )

        metric_results = {metric.name: metric for metric in result.metrics}

        for metric_name, metric in metric_results.items():
            checks.append(
                ValidationCheck(
                    check_id=f"{scenario.name}:{metric_name}",
                    name=f"{scenario.name} — {metric_name}",
                    status=(
                        CheckStatus.PASS
                        if metric.passed
                        else CheckStatus.FAIL
                    ),
                    summary=(
                        "Calculated value is within the configured "
                        "reference tolerance."
                        if metric.passed
                        else "Calculated value is outside the configured "
                        "reference tolerance."
                    ),
                    details=(
                        f"Reference={metric.expected!r}; "
                        f"absolute error={metric.absolute_error:.12g}; "
                        f"relative error={metric.relative_error:.12g}."
                    ),
                    value=metric.actual,
                    threshold=metric.tolerance,
                )
            )

    unknown_scenarios = set(actual_values) - known_names
    for scenario_name in sorted(unknown_scenarios):
        checks.append(
            ValidationCheck(
                check_id=f"unknown-scenario:{scenario_name}",
                name=f"Unrecognized scenario — {scenario_name}",
                status=CheckStatus.WARNING,
                summary="Values were supplied for an unknown reference scenario.",
                details="No reference checks were run for these values.",
            )
        )

    return MissionValidationReport(
        mission_name=mission_name,
        created_at=created_at,
        software_version=software_version,
        checks=tuple(checks),
        assumptions=assumptions,
        inputs=dict(inputs or {}),
        notes=notes,
    )