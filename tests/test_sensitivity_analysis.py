"""Tests for orbital sensitivity analysis."""

import math

import pytest

from astra.physics.constants import EARTH_MU, EARTH_RADIUS
from astra.validation.sensitivity_analysis import run_sensitivity_analysis


def _result(rows, parameter, perturbation, metric):
    return next(
        row for row in rows
        if row.parameter == parameter
        and row.perturbation_percent == perturbation
        and row.metric == metric
    )


def test_default_study_has_all_parameter_perturbation_metric_combinations():
    rows = run_sensitivity_analysis()

    assert len(rows) == 3 * 4 * 4
    assert {row.parameter for row in rows} == {
        "initial_radius", "final_radius", "earth_mu"
    }
    assert {row.perturbation_percent for row in rows} == {
        -5.0, -1.0, 1.0, 5.0
    }
    assert {row.metric for row in rows} == {
        "circular_speed_m_s",
        "orbital_period_s",
        "hohmann_total_delta_v_m_s",
        "hohmann_transfer_time_s",
    }


@pytest.mark.parametrize("perturbation", [-5.0, -1.0, 1.0, 5.0])
def test_gravitational_parameter_changes_follow_analytical_scaling(perturbation):
    rows = run_sensitivity_analysis(perturbations_percent=(perturbation,))
    factor = 1.0 + perturbation / 100.0

    speed = _result(
        rows, "earth_mu", perturbation, "circular_speed_m_s"
    )
    period = _result(
        rows, "earth_mu", perturbation, "orbital_period_s"
    )
    delta_v = _result(
        rows, "earth_mu", perturbation, "hohmann_total_delta_v_m_s"
    )
    transfer_time = _result(
        rows, "earth_mu", perturbation, "hohmann_transfer_time_s"
    )

    assert speed.perturbed_value / speed.baseline_value == pytest.approx(
        math.sqrt(factor), rel=1e-12
    )
    assert period.perturbed_value / period.baseline_value == pytest.approx(
        1.0 / math.sqrt(factor), rel=1e-12
    )
    assert delta_v.perturbed_value / delta_v.baseline_value == pytest.approx(
        math.sqrt(factor), rel=1e-12
    )
    assert transfer_time.perturbed_value / transfer_time.baseline_value == pytest.approx(
        1.0 / math.sqrt(factor), rel=1e-12
    )


@pytest.mark.parametrize("perturbation", [-5.0, -1.0, 1.0, 5.0])
def test_initial_radius_changes_speed_and_period_in_expected_directions(perturbation):
    rows = run_sensitivity_analysis(perturbations_percent=(perturbation,))

    speed = _result(
        rows, "initial_radius", perturbation, "circular_speed_m_s"
    )
    period = _result(
        rows, "initial_radius", perturbation, "orbital_period_s"
    )

    if perturbation > 0:
        assert speed.perturbed_value < speed.baseline_value
        assert period.perturbed_value > period.baseline_value
    else:
        assert speed.perturbed_value > speed.baseline_value
        assert period.perturbed_value < period.baseline_value


@pytest.mark.parametrize("perturbation", [-5.0, -1.0, 1.0, 5.0])
def test_final_radius_changes_return_finite_positive_metrics(perturbation):
    rows = run_sensitivity_analysis(perturbations_percent=(perturbation,))

    final_radius_rows = [
        row for row in rows if row.parameter == "final_radius"
    ]
    assert len(final_radius_rows) == 4
    assert all(math.isfinite(row.perturbed_value) for row in final_radius_rows)
    assert all(row.perturbed_value > 0 for row in final_radius_rows)


def test_reported_absolute_and_relative_changes_are_consistent():
    rows = run_sensitivity_analysis()

    for row in rows:
        assert row.absolute_change == pytest.approx(
            row.perturbed_value - row.baseline_value, rel=1e-12, abs=1e-12
        )
        assert row.relative_change_percent == pytest.approx(
            row.absolute_change / row.baseline_value * 100.0,
            rel=1e-12,
            abs=1e-12,
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"initial_altitude_m": float("nan")},
        {"final_altitude_m": float("inf")},
        {"earth_mu_m3_s2": 0.0},
        {"perturbations_percent": ()},
        {"perturbations_percent": (-100.0,)},
        {"perturbations_percent": (float("nan"),)},
    ],
)
def test_invalid_inputs_are_rejected(kwargs):
    with pytest.raises(ValueError):
        run_sensitivity_analysis(**kwargs)


def test_study_rejects_perturbation_that_makes_orbits_equal():
    initial_altitude = 400_000.0
    final_altitude = 800_000.0
    initial_radius = EARTH_RADIUS + initial_altitude
    final_radius = EARTH_RADIUS + final_altitude
    percent_to_match = (initial_radius / final_radius - 1.0) * 100.0

    with pytest.raises(ValueError, match="radii equal"):
        run_sensitivity_analysis(
            initial_altitude_m=initial_altitude,
            final_altitude_m=final_altitude,
            perturbations_percent=(percent_to_match,),
        )


def test_baseline_uses_astra_earth_gravitational_parameter():
    rows = run_sensitivity_analysis(perturbations_percent=(1.0,))
    baseline_speed = _result(
        rows, "earth_mu", 1.0, "circular_speed_m_s"
    ).baseline_value

    expected = math.sqrt(
        EARTH_MU / (EARTH_RADIUS + 400_000.0)
    )
    assert baseline_speed == pytest.approx(expected, rel=1e-12)
