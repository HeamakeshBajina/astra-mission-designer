"""Tests for reproducible external benchmark reports."""

import json

import pytest

from astra.validation.benchmark_report import (
    BenchmarkReference,
    build_benchmark_report,
)
from astra.validation.mission_report import CheckStatus


def make_benchmark(**overrides):
    values = {
        "benchmark_id": "leo-speed",
        "name": "Circular orbital speed",
        "reference_value": 7668.6,
        "unit": "m/s",
        "source_name": "Published reference",
        "source_url": "https://example.org/orbit-reference",
        "absolute_tolerance": 0.1,
        "relative_tolerance": 1e-5,
    }
    values.update(overrides)
    return BenchmarkReference(**values)


def make_report(benchmarks, actual_values):
    return build_benchmark_report(
        mission_name="LEO benchmark",
        created_at="2026-10-18T00:00:00Z",
        software_version="0.2.0",
        benchmarks=tuple(benchmarks),
        actual_values=actual_values,
        inputs={"altitude_m": 400_000},
    )


def test_value_within_absolute_tolerance_passes():
    report = make_report([make_benchmark()], {"leo-speed": 7668.65})
    assert report.checks[0].status is CheckStatus.PASS


def test_value_within_relative_tolerance_passes():
    benchmark = make_benchmark(
        absolute_tolerance=0.0,
        relative_tolerance=1e-4,
    )
    report = make_report([benchmark], {"leo-speed": 7669.0})
    assert report.checks[0].status is CheckStatus.PASS


def test_value_outside_both_tolerances_fails():
    benchmark = make_benchmark(
        absolute_tolerance=0.01,
        relative_tolerance=1e-8,
    )
    report = make_report([benchmark], {"leo-speed": 7700.0})
    assert report.checks[0].status is CheckStatus.FAIL
    assert report.status is CheckStatus.FAIL


def test_missing_value_is_not_run():
    report = make_report([make_benchmark()], {})
    assert report.checks[0].status is CheckStatus.NOT_RUN
    assert report.status is CheckStatus.NOT_RUN


def test_unknown_value_is_warning_not_pass():
    report = make_report([], {"unknown-case": 123.0})
    assert report.checks[0].status is CheckStatus.WARNING


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), "7668.6"])
def test_invalid_actual_value_is_rejected(value):
    with pytest.raises(ValueError, match="finite real number"):
        make_report([make_benchmark()], {"leo-speed": value})


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), "1"])
def test_invalid_reference_value_is_rejected(value):
    with pytest.raises(ValueError, match="finite real number"):
        make_benchmark(reference_value=value)


@pytest.mark.parametrize("tolerance", [-1.0, float("nan"), float("inf"), True])
def test_invalid_tolerance_is_rejected(tolerance):
    with pytest.raises(ValueError):
        make_benchmark(absolute_tolerance=tolerance)


def test_invalid_source_url_is_rejected():
    with pytest.raises(ValueError, match="HTTP"):
        make_benchmark(source_url="not-a-url")


def test_duplicate_benchmark_ids_are_rejected():
    benchmark = make_benchmark()
    with pytest.raises(ValueError, match="unique"):
        make_report([benchmark, benchmark], {"leo-speed": 7668.6})


def test_zero_reference_uses_absolute_tolerance_without_division_by_zero():
    benchmark = make_benchmark(
        reference_value=0.0,
        absolute_tolerance=1e-6,
        relative_tolerance=0.0,
    )
    report = make_report([benchmark], {"leo-speed": 5e-7})
    assert report.checks[0].status is CheckStatus.PASS
    assert "undefined for a zero reference value" in report.checks[0].details


def test_zero_reference_outside_absolute_tolerance_fails():
    benchmark = make_benchmark(
        reference_value=0.0,
        absolute_tolerance=1e-6,
        relative_tolerance=1.0,
    )
    report = make_report([benchmark], {"leo-speed": 1e-4})
    assert report.checks[0].status is CheckStatus.FAIL


def test_json_and_markdown_include_reference_provenance():
    report = make_report([make_benchmark()], {"leo-speed": 7668.6})

    payload = json.loads(report.to_json())
    assert payload["checks"][0]["status"] == "PASS"
    assert "https://example.org/orbit-reference" in payload["checks"][0]["details"]

    markdown = report.to_markdown()
    assert "https://example.org/orbit-reference" in markdown
    assert "not proof of flight readiness" in markdown


def test_json_report_is_strict_and_deterministic():
    report = make_report([make_benchmark()], {"leo-speed": 7668.6})
    first = report.to_json()
    second = report.to_json()

    assert first == second
    assert "NaN" not in first
    assert "Infinity" not in first


def test_invalid_actual_value_key_is_rejected():
    with pytest.raises(ValueError, match="keys"):
        make_report([make_benchmark()], {"": 7668.6})


def test_relative_tolerance_can_pass_when_absolute_error_is_large():
    benchmark = make_benchmark(
        reference_value=1_000_000.0,
        absolute_tolerance=0.1,
        relative_tolerance=1e-3,
    )
    report = make_report([benchmark], {"leo-speed": 1_000_500.0})
    assert report.checks[0].status is CheckStatus.PASS
