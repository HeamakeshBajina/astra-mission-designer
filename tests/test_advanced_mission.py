"""Tests for advanced mission analysis."""

import pytest

from astra.mission.advanced_mission import (
    analyze_advanced_mission,
)


def test_advanced_mission_without_plane_change_matches_hohmann():
    result = analyze_advanced_mission(
        initial_radius=6_771_000,
        final_radius=7_171_000,
        inclination_change=0,
    )

    assert result.plane_change_delta_v == pytest.approx(0.0)
    assert result.combined_delta_v == pytest.approx(
        result.hohmann_delta_v
    )


def test_advanced_mission_includes_plane_change():
    result = analyze_advanced_mission(
        initial_radius=6_771_000,
        final_radius=7_171_000,
        inclination_change=10,
    )

    assert result.hohmann_delta_v > 0
    assert result.plane_change_delta_v > 0
    assert result.combined_delta_v > result.hohmann_delta_v


def test_transfer_time_is_positive():
    result = analyze_advanced_mission(
        initial_radius=6_771_000,
        final_radius=7_171_000,
        inclination_change=10,
    )

    assert result.transfer_time > 0


def test_invalid_initial_radius_is_rejected():
    with pytest.raises(ValueError):
        analyze_advanced_mission(
            initial_radius=0,
            final_radius=7_171_000,
            inclination_change=10,
        )


def test_invalid_final_radius_is_rejected():
    with pytest.raises(ValueError):
        analyze_advanced_mission(
            initial_radius=6_771_000,
            final_radius=0,
            inclination_change=10,
        )


def test_negative_inclination_is_rejected():
    with pytest.raises(ValueError):
        analyze_advanced_mission(
            initial_radius=6_771_000,
            final_radius=7_171_000,
            inclination_change=-5,
        )