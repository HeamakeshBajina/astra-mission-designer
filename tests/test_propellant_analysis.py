"""Tests for propellant-constrained mission analysis."""

import pytest

from astra.mission.propellant_analysis import (
    evaluate_propellant_feasibility,
)


def test_mission_is_feasible_with_sufficient_propellant():
    result = evaluate_propellant_feasibility(
        dry_mass=500,
        propellant_available=500,
        specific_impulse=300,
        required_delta_v=1_000,
    )

    assert result.feasible is True
    assert result.propellant_required > 0
    assert result.propellant_remaining > 0


def test_mission_is_infeasible_with_insufficient_propellant():
    result = evaluate_propellant_feasibility(
        dry_mass=1_000,
        propellant_available=10,
        specific_impulse=200,
        required_delta_v=5_000,
    )

    assert result.feasible is False
    assert result.propellant_remaining < 0


def test_zero_delta_v_requires_no_propellant():
    result = evaluate_propellant_feasibility(
        dry_mass=500,
        propellant_available=100,
        specific_impulse=300,
        required_delta_v=0,
    )

    assert result.propellant_required == pytest.approx(0)
    assert result.propellant_remaining == pytest.approx(100)
    assert result.feasible is True


def test_initial_mass_is_dry_mass_plus_propellant():
    result = evaluate_propellant_feasibility(
        dry_mass=700,
        propellant_available=300,
        specific_impulse=300,
        required_delta_v=1_000,
    )

    assert result.initial_mass == pytest.approx(1_000)


def test_negative_dry_mass_is_rejected():
    with pytest.raises(ValueError):
        evaluate_propellant_feasibility(
            dry_mass=-1,
            propellant_available=500,
            specific_impulse=300,
            required_delta_v=1_000,
        )


def test_negative_propellant_is_rejected():
    with pytest.raises(ValueError):
        evaluate_propellant_feasibility(
            dry_mass=500,
            propellant_available=-1,
            specific_impulse=300,
            required_delta_v=1_000,
        )


def test_invalid_specific_impulse_is_rejected():
    with pytest.raises(ValueError):
        evaluate_propellant_feasibility(
            dry_mass=500,
            propellant_available=500,
            specific_impulse=0,
            required_delta_v=1_000,
        )


def test_negative_delta_v_is_rejected():
    with pytest.raises(ValueError):
        evaluate_propellant_feasibility(
            dry_mass=500,
            propellant_available=500,
            specific_impulse=300,
            required_delta_v=-1,
        )