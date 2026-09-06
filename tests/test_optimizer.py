import pytest

from astra.mission.optimizer import (
    optimize_transfer_strategy,
)


def test_optimizer_includes_hohmann_strategy():
    result = optimize_transfer_strategy(
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
        minimum_intermediate_altitude=900_000,
        maximum_intermediate_altitude=5_000_000,
        step=500_000,
    )

    strategies = [
        candidate.strategy
        for candidate in result.candidates
    ]

    assert "Hohmann" in strategies


def test_optimizer_includes_bielliptic_candidates():
    result = optimize_transfer_strategy(
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
        minimum_intermediate_altitude=900_000,
        maximum_intermediate_altitude=5_000_000,
        step=500_000,
    )

    bielliptic_candidates = [
        candidate
        for candidate in result.candidates
        if candidate.strategy == "Bi-elliptic"
    ]

    assert len(bielliptic_candidates) > 0


def test_optimizer_returns_feasible_result():
    result = optimize_transfer_strategy(
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
        minimum_intermediate_altitude=900_000,
        maximum_intermediate_altitude=5_000_000,
        step=500_000,
    )

    assert result.best_candidate.feasible is True


def test_low_altitude_ratio_prefers_hohmann():
    result = optimize_transfer_strategy(
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
        minimum_intermediate_altitude=900_000,
        maximum_intermediate_altitude=5_000_000,
        step=500_000,
    )

    assert result.best_candidate.strategy == "Hohmann"


def test_best_candidate_has_lowest_feasible_delta_v():
    result = optimize_transfer_strategy(
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
        minimum_intermediate_altitude=900_000,
        maximum_intermediate_altitude=5_000_000,
        step=500_000,
    )

    feasible_candidates = [
        candidate
        for candidate in result.candidates
        if candidate.feasible
    ]

    minimum_delta_v = min(
        candidate.total_delta_v
        for candidate in feasible_candidates
    )

    assert result.best_candidate.total_delta_v == pytest.approx(
        minimum_delta_v
    )


def test_candidate_propellant_is_positive():
    result = optimize_transfer_strategy(
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
        minimum_intermediate_altitude=900_000,
        maximum_intermediate_altitude=5_000_000,
        step=500_000,
    )

    for candidate in result.candidates:
        assert candidate.required_propellant > 0


def test_optimizer_rejects_lowering_transfer():
    with pytest.raises(ValueError):
        optimize_transfer_strategy(
            initial_altitude=800_000,
            final_altitude=400_000,
            spacecraft_mass=1_000,
            specific_impulse=300,
            available_propellant=500,
            minimum_intermediate_altitude=900_000,
            maximum_intermediate_altitude=5_000_000,
            step=500_000,
        )


def test_optimizer_rejects_invalid_step():
    with pytest.raises(ValueError):
        optimize_transfer_strategy(
            initial_altitude=400_000,
            final_altitude=800_000,
            spacecraft_mass=1_000,
            specific_impulse=300,
            available_propellant=500,
            minimum_intermediate_altitude=900_000,
            maximum_intermediate_altitude=5_000_000,
            step=0,
        )


def test_optimizer_rejects_invalid_range():
    with pytest.raises(ValueError):
        optimize_transfer_strategy(
            initial_altitude=400_000,
            final_altitude=800_000,
            spacecraft_mass=1_000,
            specific_impulse=300,
            available_propellant=500,
            minimum_intermediate_altitude=5_000_000,
            maximum_intermediate_altitude=900_000,
            step=500_000,
        )


def test_optimizer_rejects_no_feasible_strategy():
    with pytest.raises(ValueError):
        optimize_transfer_strategy(
            initial_altitude=400_000,
            final_altitude=800_000,
            spacecraft_mass=1_000,
            specific_impulse=300,
            available_propellant=0,
            minimum_intermediate_altitude=900_000,
            maximum_intermediate_altitude=5_000_000,
            step=500_000,
        )