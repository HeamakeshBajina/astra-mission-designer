import pytest

from astra.mission.analysis import analyze_hohmann_mission


def test_mission_is_feasible_with_sufficient_delta_v():
    result = analyze_hohmann_mission(
        initial_altitude=400_000,
        final_altitude=800_000,
        available_delta_v=2_000,
    )

    assert result.feasible is True


def test_mission_is_infeasible_with_insufficient_delta_v():
    result = analyze_hohmann_mission(
        initial_altitude=400_000,
        final_altitude=800_000,
        available_delta_v=100,
    )

    assert result.feasible is False


def test_mission_has_positive_delta_v():
    result = analyze_hohmann_mission(
        initial_altitude=400_000,
        final_altitude=800_000,
        available_delta_v=2_000,
    )

    assert result.total_delta_v > 0


def test_invalid_delta_v():
    with pytest.raises(ValueError):
        analyze_hohmann_mission(
            initial_altitude=400_000,
            final_altitude=800_000,
            available_delta_v=-1,
        )


def test_invalid_altitude():
    with pytest.raises(ValueError):
        analyze_hohmann_mission(
            initial_altitude=-1,
            final_altitude=800_000,
            available_delta_v=2_000,
        )