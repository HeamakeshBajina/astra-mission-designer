"""Integration tests for ASTRA reference-scenario mission reports."""

import pytest

from astra.validation.mission_report import CheckStatus
from astra.validation.mission_report_builder import (
    build_reference_mission_report,
)
from astra.validation.reference_scenarios import all_reference_scenarios


def make_report(actual_values):
    return build_reference_mission_report(
        mission_name="Reference validation test",
        created_at="2026-10-18T00:00:00Z",
        software_version="0.1.0",
        actual_values=actual_values,
    )


def test_missing_calculations_are_not_run():
    report = make_report({})

    assert report.checks
    assert report.status is CheckStatus.NOT_RUN
    assert all(
        check.status is CheckStatus.NOT_RUN
        for check in report.checks
    )


def test_reference_values_pass_when_supplied_as_calculated_values():
    scenarios = all_reference_scenarios()
    actual_values = {
        scenario.name: dict(scenario.expected_values)
        for scenario in scenarios
    }

    report = make_report(actual_values)

    assert report.status is CheckStatus.PASS
    assert all(check.status is CheckStatus.PASS for check in report.checks)


def test_incorrect_value_fails_its_check():
    scenario = all_reference_scenarios()[0]
    actual = dict(scenario.expected_values)
    actual["velocity"] *= 1.1

    report = make_report({scenario.name: actual})

    velocity_check = next(
        check for check in report.checks
        if check.check_id == f"{scenario.name}:velocity"
    )
    assert velocity_check.status is CheckStatus.FAIL
    assert report.status is CheckStatus.FAIL


def test_missing_metric_is_not_run_while_supplied_metrics_are_checked():
    scenario = all_reference_scenarios()[0]
    actual = {"velocity": scenario.expected_values["velocity"]}

    report = make_report({scenario.name: actual})

    radius_check = next(
        check for check in report.checks
        if check.check_id == f"{scenario.name}:radius"
    )
    velocity_check = next(
        check for check in report.checks
        if check.check_id == f"{scenario.name}:velocity"
    )

    assert radius_check.status is CheckStatus.NOT_RUN
    assert velocity_check.status is CheckStatus.PASS
    assert report.status is CheckStatus.NOT_RUN


def test_unknown_scenario_is_warning_not_pass():
    report = make_report({"Imaginary Scenario": {"value": 123.0}})

    assert report.status is CheckStatus.WARNING
    assert any(
        check.status is CheckStatus.WARNING
        for check in report.checks
    )


def test_unexpected_metric_name_is_rejected():
    scenario = all_reference_scenarios()[0]

    with pytest.raises(ValueError, match="Unexpected metrics"):
        make_report({
            scenario.name: {
                **scenario.expected_values,
                "made_up_metric": 1.0,
            }
        })


def test_non_finite_calculated_value_is_rejected():
    scenario = all_reference_scenarios()[0]

    with pytest.raises(ValueError, match="must be finite"):
        make_report({
            scenario.name: {
                **scenario.expected_values,
                "velocity": float("nan"),
            }
        })


def test_report_keeps_mission_metadata():
    report = build_reference_mission_report(
        mission_name="Metadata check",
        created_at="2026-10-18T00:00:00Z",
        software_version="0.1.0",
        actual_values={},
        inputs={"altitude_km": 400},
        assumptions=("Two-body model.",),
        notes=("Test report.",),
    )

    payload = report.to_dict()
    assert payload["mission_name"] == "Metadata check"
    assert payload["inputs"]["altitude_km"] == 400
    assert payload["assumptions"] == ["Two-body model."]
    assert payload["notes"] == ["Test report."]