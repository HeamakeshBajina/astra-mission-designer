import json
import pytest

from astra.validation.sensitivity_analysis import run_sensitivity_analysis
from astra.validation.sensitivity_report import (
    build_sensitivity_report,
    sensitivity_report_to_json,
    sensitivity_report_to_markdown,
)


@pytest.fixture
def results():
    return run_sensitivity_analysis()


def test_report_contains_expected_sections(results):
    report = build_sensitivity_report(results)
    assert report["report_name"] == "ASTRA Orbital Sensitivity Analysis"
    assert report["baseline_metrics"]
    assert report["rankings"]
    assert report["results"]
    assert report["limitations"]


def test_report_contains_all_rows(results):
    report = build_sensitivity_report(results)
    assert len(report["results"]) == len(results) == 48


def test_rankings_are_descending(results):
    report = build_sensitivity_report(results)
    for ranking in report["rankings"].values():
        scores = [item["max_absolute_relative_change_percent"] for item in ranking]
        assert scores == sorted(scores, reverse=True)


def test_ranking_scores_match_observed_results(results):
    report = build_sensitivity_report(results)
    for metric, ranking in report["rankings"].items():
        for item in ranking:
            observed = [
                abs(row.relative_change_percent)
                for row in results
                if row.metric == metric and row.parameter == item["parameter"]
            ]
            assert item["max_absolute_relative_change_percent"] == max(observed)


def test_json_is_valid_and_deterministic(results):
    first = sensitivity_report_to_json(results)
    assert first == sensitivity_report_to_json(results)
    assert json.loads(first)["results"]


def test_json_rejects_invalid_indent(results):
    with pytest.raises(ValueError):
        sensitivity_report_to_json(results, indent=-1)
    with pytest.raises(ValueError):
        sensitivity_report_to_json(results, indent=True)


def test_markdown_contains_tables_and_limitations(results):
    markdown = sensitivity_report_to_markdown(results)
    assert "# ASTRA Orbital Sensitivity Analysis" in markdown
    assert "## Baseline metrics" in markdown
    assert "## Sensitivity rankings" in markdown
    assert "## Perturbation results" in markdown
    assert "## Limitations" in markdown


def test_empty_results_are_rejected():
    with pytest.raises(ValueError, match="At least one"):
        build_sensitivity_report([])


def test_report_is_deterministic(results):
    assert build_sensitivity_report(results) == build_sensitivity_report(results)


def test_detail_rows_are_sorted(results):
    report = build_sensitivity_report(results)
    keys = [
        (item["metric"], item["parameter"], item["perturbation_percent"])
        for item in report["results"]
    ]
    assert keys == sorted(keys)
