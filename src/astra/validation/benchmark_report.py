"""Reproducible benchmark reports using documented external references."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
from numbers import Real
from typing import Any
from urllib.parse import urlparse

from astra.validation.mission_report import (
    CheckStatus,
    MissionValidationReport,
    ValidationCheck,
)


def _finite_number(value: object, label: str) -> float:
    """Return a finite real number, explicitly excluding booleans."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a finite real number.")

    try:
        result = float(value)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a finite real number.") from exc

    if not math.isfinite(result):
        raise ValueError(f"{label} must be a finite real number.")

    return result


@dataclass(frozen=True)
class BenchmarkReference:
    """An externally documented reference and its acceptance criteria."""

    benchmark_id: str
    name: str
    reference_value: float
    unit: str
    source_name: str
    source_url: str
    absolute_tolerance: float
    relative_tolerance: float

    def __post_init__(self) -> None:
        for label in ("benchmark_id", "name", "unit", "source_name", "source_url"):
            value = getattr(self, label)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{label} cannot be empty.")

        parsed_url = urlparse(self.source_url)
        if (
            parsed_url.scheme not in {"http", "https"}
            or not parsed_url.netloc
            or any(character.isspace() for character in self.source_url)
        ):
            raise ValueError("source_url must be an absolute HTTP(S) URL.")

        for label in ("reference_value", "absolute_tolerance", "relative_tolerance"):
            value = _finite_number(getattr(self, label), label)
            object.__setattr__(self, label, value)

        if self.absolute_tolerance < 0 or self.relative_tolerance < 0:
            raise ValueError("Benchmark tolerances must be nonnegative.")


def build_benchmark_report(
    *,
    mission_name: str,
    created_at: str,
    software_version: str,
    benchmarks: tuple[BenchmarkReference, ...],
    actual_values: Mapping[str, float],
    inputs: Mapping[str, Any] | None = None,
    assumptions: tuple[str, ...] = (
        "Reference values and source metadata are supplied by the caller.",
        "ASTRA does not independently authenticate the cited source.",
        "A check passes when either its absolute or relative tolerance is met.",
        "Passing checks apply only to the stated model and tolerances.",
        "This report is not proof of flight readiness or spacecraft safety.",
    ),
    notes: tuple[str, ...] = (),
) -> MissionValidationReport:
    """Compare calculated values with documented external benchmarks.

    Values are keyed by benchmark_id. Missing values become NOT_RUN.
    A comparison passes when absolute error <= absolute_tolerance OR,
    for a nonzero reference, relative error <= relative_tolerance.
    """
    if not isinstance(actual_values, Mapping):
        raise ValueError("actual_values must be a mapping.")

    ids = [benchmark.benchmark_id for benchmark in benchmarks]
    if len(ids) != len(set(ids)):
        raise ValueError("Benchmark IDs must be unique.")

    if any(not isinstance(key, str) or not key.strip() for key in actual_values):
        raise ValueError("Calculated-value keys must be nonempty strings.")

    normalized_values: dict[str, float] = {}
    for key, value in actual_values.items():
        normalized_values[key] = _finite_number(
            value, f"Calculated value for {key}"
        )

    known_ids = set(ids)
    checks: list[ValidationCheck] = []

    for benchmark in benchmarks:
        benchmark_id = benchmark.benchmark_id

        if benchmark_id not in normalized_values:
            checks.append(
                ValidationCheck(
                    check_id=benchmark_id,
                    name=benchmark.name,
                    status=CheckStatus.NOT_RUN,
                    summary="No calculated value was supplied.",
                    details=(
                        f"Reference source: {benchmark.source_name} "
                        f"({benchmark.source_url})."
                    ),
                    threshold=(
                        f"absolute error <= {benchmark.absolute_tolerance}; "
                        f"OR relative error <= {benchmark.relative_tolerance}"
                    ),
                    unit=benchmark.unit,
                )
            )
            continue

        actual = normalized_values[benchmark_id]
        reference = benchmark.reference_value

        absolute_error = abs(actual - reference)
        relative_error = (
            absolute_error / abs(reference)
            if reference != 0
            else None
        )

        # Relative tolerance is undefined for a zero reference.
        passed = absolute_error <= benchmark.absolute_tolerance
        if relative_error is not None:
            passed = passed or (
                relative_error <= benchmark.relative_tolerance
            )

        relative_text = (
            "undefined for a zero reference value"
            if relative_error is None
            else f"{relative_error:.12g}"
        )
        details = (
            f"Reference value={reference:.12g} {benchmark.unit}; "
            f"absolute error={absolute_error:.12g}; "
            f"relative error={relative_text}; "
            f"source={benchmark.source_name}; "
            f"source URL={benchmark.source_url}."
        )

        checks.append(
            ValidationCheck(
                check_id=benchmark_id,
                name=benchmark.name,
                status=CheckStatus.PASS if passed else CheckStatus.FAIL,
                summary=(
                    "At least one configured error tolerance was met."
                    if passed
                    else "Neither configured error tolerance was met."
                ),
                details=details,
                value=actual,
                unit=benchmark.unit,
                threshold=(
                    f"absolute error <= {benchmark.absolute_tolerance}; "
                    f"OR relative error <= {benchmark.relative_tolerance}"
                ),
            )
        )

    for unknown_id in sorted(set(normalized_values) - known_ids):
        checks.append(
            ValidationCheck(
                check_id=f"unknown-benchmark:{unknown_id}",
                name=f"Unrecognized benchmark: {unknown_id}",
                status=CheckStatus.WARNING,
                summary="A calculated value has no matching benchmark definition.",
                details="No numerical comparison was performed for this value.",
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
