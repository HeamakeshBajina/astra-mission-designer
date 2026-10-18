"""Tests for mission target-altitude sensitivity analysis."""

import json
import math

import pytest

from astra.mission.altitude_sensitivity import analyze_altitude_sensitivity


def run(**overrides):
    args = dict(
        initial_altitude_km=400,
        minimum_target_altitude_km=600,
        maximum_target_altitude_km=1600,
        sample_count=11,
        max_delta_v_m_s=5000,
        max_transfer_time_s=200000,
    )
    args.update(overrides)
    return analyze_altitude_sensitivity(**args)


def test_sweep_includes_both_endpoints_and_requested_count():
    report = run()
    assert len(report.points) == 11
    assert report.points[0].target_altitude_km == pytest.approx(600)
    assert report.points[-1].target_altitude_km == pytest.approx(1600)


def test_targets_are_uniformly_spaced():
    points = run().points
    gaps = [
        points[i + 1].target_altitude_km - points[i].target_altitude_km
        for i in range(len(points) - 1)
    ]
    assert all(gap == pytest.approx(100) for gap in gaps)


def test_results_are_finite_and_positive():
    for point in run().points:
        assert math.isfinite(point.total_delta_v_m_s)
        assert point.total_delta_v_m_s > 0
        assert math.isfinite(point.transfer_time_s)
        assert point.transfer_time_s > 0


def test_feasibility_matches_both_constraint_checks():
    for point in run().points:
        assert point.feasible == (point.delta_v_passed and point.time_passed)


def test_tighter_delta_v_budget_cannot_increase_feasible_count():
    loose = run(max_delta_v_m_s=5000)
    tight = run(max_delta_v_m_s=100)
    assert sum(p.feasible for p in tight.points) <= sum(
        p.feasible for p in loose.points
    )


def test_tighter_time_limit_cannot_increase_feasible_count():
    loose = run(max_transfer_time_s=200000)
    tight = run(max_transfer_time_s=1000)
    assert sum(p.feasible for p in tight.points) <= sum(
        p.feasible for p in loose.points
    )


def test_report_is_json_serializable_and_documents_limitations():
    data = run().to_dict()
    decoded = json.loads(json.dumps(data))
    assert decoded["sample_count"] == 11
    assert len(decoded["points"]) == 11
    assert decoded["limitations"]


@pytest.mark.parametrize("count", [0, 1, 501, True, 2.5])
def test_invalid_sample_count_rejected(count):
    with pytest.raises(ValueError):
        run(sample_count=count)


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True])
def test_invalid_initial_altitude_rejected(value):
    with pytest.raises(ValueError):
        run(initial_altitude_km=value)


def test_invalid_range_rejected():
    with pytest.raises(ValueError):
        run(
            minimum_target_altitude_km=1000,
            maximum_target_altitude_km=1000,
        )


def test_sweep_rejects_a_sample_equal_to_initial_altitude():
    with pytest.raises(ValueError, match="must not equal"):
        run(
            minimum_target_altitude_km=400,
            maximum_target_altitude_km=800,
            sample_count=5,
        )
