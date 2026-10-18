"""Integration tests for ASTRA's externally sourced orbital benchmarks."""

import json

import pytest

from astra.validation.mission_report import CheckStatus
from astra.validation.orbital_benchmark_suite import (
    JPL_DE440_GM_URL,
    NASA_EARTH_FACTSHEET_URL,
    ORBITAL_BENCHMARKS,
    build_core_orbital_benchmark_report,
    calculate_core_orbital_values,
)


def test_catalogue_contains_seven_unique_benchmarks():
    ids = [item.benchmark_id for item in ORBITAL_BENCHMARKS]
    assert len(ids) == 7
    assert len(ids) == len(set(ids))


def test_every_benchmark_has_external_provenance_and_units():
    for benchmark in ORBITAL_BENCHMARKS:
        assert benchmark.source_url.startswith("https://")
        assert benchmark.source_name
        assert benchmark.unit
        assert benchmark.absolute_tolerance >= 0
        assert benchmark.relative_tolerance >= 0

    urls = {item.source_url for item in ORBITAL_BENCHMARKS}
    assert JPL_DE440_GM_URL in urls
    assert NASA_EARTH_FACTSHEET_URL in urls


def test_calculated_values_cover_every_catalogue_id():
    values = calculate_core_orbital_values()
    ids = {item.benchmark_id for item in ORBITAL_BENCHMARKS}

    assert set(values) == ids
    assert all(value > 0 for value in values.values())


def test_core_report_passes_all_reference_checks():
    report = build_core_orbital_benchmark_report(
        created_at="2026-10-18T00:00:00Z",
        software_version="0.2.0",
    )

    assert len(report.checks) == 7
    assert report.status is CheckStatus.PASS
    assert all(check.status is CheckStatus.PASS for check in report.checks)


def test_report_records_model_assumptions_and_inputs():
    report = build_core_orbital_benchmark_report(
        created_at="2026-10-18T00:00:00Z",
        software_version="0.2.0",
    )

    assert report.inputs["model"] == "ideal two-body dynamics"
    assert report.inputs["initial_altitude_m"] == 400_000.0
    assert any("JPL DE440" in item for item in report.assumptions)
    assert any("not direct" in item for item in report.notes)


def test_report_json_includes_reference_urls_and_statuses():
    report = build_core_orbital_benchmark_report(
        created_at="2026-10-18T00:00:00Z",
        software_version="0.2.0",
    )

    payload = json.loads(report.to_json())
    assert payload["overall_status"] == "PASS"
    assert len(payload["checks"]) == 7

    all_details = "\n".join(item["details"] for item in payload["checks"])
    assert JPL_DE440_GM_URL in all_details
    assert NASA_EARTH_FACTSHEET_URL in all_details


@pytest.mark.parametrize(
    "benchmark_id",
    [
        "leo400.circular_speed",
        "leo400.escape_speed",
        "leo400.orbital_period",
        "hohmann400_800.first_burn",
        "hohmann400_800.second_burn",
        "hohmann400_800.total_delta_v",
        "hohmann400_800.transfer_time",
    ],
)
def test_reference_values_are_finite_and_positive(benchmark_id):
    benchmark = next(
        item for item in ORBITAL_BENCHMARKS
        if item.benchmark_id == benchmark_id
    )
    assert benchmark.reference_value > 0
    assert benchmark.reference_value < float("inf")
