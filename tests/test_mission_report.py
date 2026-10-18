"""Tests for structured ASTRA mission validation reports."""

import json

import pytest

from astra.validation.mission_report import (
    CheckStatus,
    MissionValidationReport,
    ValidationCheck,
)


def make_check(status=CheckStatus.PASS, check_id="orbit-001"):
    return ValidationCheck(
        check_id=check_id,
        name="Circular orbit check",
        status=status,
        summary="Orbital velocity compared with the reference value.",
        value=7.67,
        unit="km/s",
        threshold=0.01,
    )


def make_report(checks=()):
    return MissionValidationReport(
        mission_name="LEO demonstration",
        created_at="2026-10-18T00:00:00Z",
        software_version="0.1.0",
        checks=tuple(checks),
        assumptions=("Two-body point-mass Earth model.",),
        inputs={"altitude_km": 400, "inclination_deg": 51.6},
        notes=("Demonstration only; not flight-qualified.",),
    )


def test_all_pass_checks_produce_pass_report():
    report = make_report([make_check()])
    assert report.status is CheckStatus.PASS


def test_failure_takes_precedence_over_warning():
    report = make_report([
        make_check(CheckStatus.WARNING, "warning-001"),
        make_check(CheckStatus.FAIL, "failure-001"),
    ])
    assert report.status is CheckStatus.FAIL


def test_warning_takes_precedence_over_not_run():
    report = make_report([
        make_check(CheckStatus.NOT_RUN, "not-run-001"),
        make_check(CheckStatus.WARNING, "warning-001"),
    ])
    assert report.status is CheckStatus.WARNING


def test_empty_report_is_not_run_not_pass():
    assert make_report().status is CheckStatus.NOT_RUN


def test_not_run_check_does_not_count_as_pass():
    report = make_report([make_check(CheckStatus.NOT_RUN)])
    assert report.status is CheckStatus.NOT_RUN
    assert report.summary_counts["NOT RUN"] == 1
    assert report.summary_counts["PASS"] == 0


def test_json_round_trips_and_includes_schema_version():
    report = make_report([make_check()])
    payload = json.loads(report.to_json())

    assert payload["schema_version"] == "1.0"
    assert payload["overall_status"] == "PASS"
    assert payload["checks"][0]["status"] == "PASS"
    assert payload["inputs"]["altitude_km"] == 400


def test_json_output_is_deterministic():
    report = make_report([make_check()])
    assert report.to_json() == report.to_json()


def test_markdown_contains_status_assumptions_and_limitation():
    markdown = make_report([make_check()]).to_markdown()

    assert "Mission Validation Report: LEO demonstration" in markdown
    assert "**Overall status:** PASS" in markdown
    assert "Two-body point-mass Earth model." in markdown
    assert "not flight-qualified" in markdown
    assert "not, by itself, proof of mission feasibility" in markdown


def test_duplicate_check_ids_are_rejected():
    with pytest.raises(ValueError, match="unique"):
        make_report([
            make_check(check_id="duplicate"),
            make_check(check_id="duplicate"),
        ])


@pytest.mark.parametrize("field,value", [
    ("mission_name", ""),
    ("created_at", ""),
    ("software_version", ""),
])
def test_required_metadata_cannot_be_empty(field, value):
    kwargs = {
        "mission_name": "Mission",
        "created_at": "2026-10-18T00:00:00Z",
        "software_version": "0.1.0",
    }
    kwargs[field] = value

    with pytest.raises(ValueError, match=field):
        MissionValidationReport(**kwargs)


def test_empty_check_id_is_rejected():
    with pytest.raises(ValueError, match="check_id"):
        make_check(check_id=" ")


def test_non_json_input_is_rejected():
    with pytest.raises(ValueError, match="JSON-serializable"):
        MissionValidationReport(
            mission_name="Mission",
            created_at="2026-10-18T00:00:00Z",
            software_version="0.1.0",
            inputs={"unsupported": object()},
        )


def test_non_finite_input_is_rejected():
    with pytest.raises(ValueError, match="JSON-serializable"):
        MissionValidationReport(
            mission_name="Mission",
            created_at="2026-10-18T00:00:00Z",
            software_version="0.1.0",
            inputs={"bad_value": float("nan")},
        )


def test_negative_json_indent_is_rejected():
    with pytest.raises(ValueError, match="indent"):
        make_report().to_json(indent=-1)


def test_markdown_handles_no_checks_and_no_inputs():
    report = MissionValidationReport(
        mission_name="Empty demonstration",
        created_at="2026-10-18T00:00:00Z",
        software_version="0.1.0",
        inputs={},
    )
    markdown = report.to_markdown()
    assert "No validation checks have been recorded." in markdown
    assert "No mission inputs recorded." in markdown