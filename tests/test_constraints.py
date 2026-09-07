"""Tests for mission constraint analysis."""

import pytest

from astra.mission.constraints import (
    evaluate_delta_v_feasibility,
)


def test_feasible_mission():
    result = evaluate_delta_v_feasibility(
        required_delta_v=4_000,
        available_delta_v=5_000,
    )

    assert result.feasible is True
    assert result.delta_v_margin == pytest.approx(1_000)


def test_infeasible_mission():
    result = evaluate_delta_v_feasibility(
        required_delta_v=6_000,
        available_delta_v=5_000,
    )

    assert result.feasible is False
    assert result.delta_v_margin == pytest.approx(-1_000)


def test_exact_delta_v_is_feasible():
    result = evaluate_delta_v_feasibility(
        required_delta_v=5_000,
        available_delta_v=5_000,
    )

    assert result.feasible is True
    assert result.delta_v_margin == pytest.approx(0)


def test_zero_delta_v_requirement():
    result = evaluate_delta_v_feasibility(
        required_delta_v=0,
        available_delta_v=5_000,
    )

    assert result.feasible is True


def test_negative_required_delta_v_is_rejected():
    with pytest.raises(ValueError):
        evaluate_delta_v_feasibility(
            required_delta_v=-1,
            available_delta_v=5_000,
        )


def test_negative_available_delta_v_is_rejected():
    with pytest.raises(ValueError):
        evaluate_delta_v_feasibility(
            required_delta_v=5_000,
            available_delta_v=-1,
        )