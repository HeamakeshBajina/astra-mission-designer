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
@pytest.mark.parametrize("inclination_change", [0, 10, 45, 90, 180])
def test_combined_delta_v_matches_arrival_velocity_geometry(
    inclination_change,
):
    import math

    from astra.physics.constants import EARTH_MU
    from astra.physics.transfers import hohmann_transfer

    initial_radius = 6_771_000
    final_radius = 7_171_000
    transfer = hohmann_transfer(initial_radius, final_radius)

    arrival_velocity = math.sqrt(
        EARTH_MU
        * (
            2 / final_radius
            - 1 / transfer.transfer_semi_major_axis
        )
    )
    target_velocity = math.sqrt(EARTH_MU / final_radius)
    angle = math.radians(inclination_change)

    expected_arrival_burn = math.sqrt(
        arrival_velocity**2
        + target_velocity**2
        - 2 * arrival_velocity * target_velocity * math.cos(angle)
    )
    expected_total = transfer.first_burn_delta_v + expected_arrival_burn

    result = analyze_advanced_mission(
        initial_radius,
        final_radius,
        inclination_change,
    )

    assert result.combined_delta_v == pytest.approx(expected_total)
    assert result.hohmann_delta_v == pytest.approx(transfer.total_delta_v)


@pytest.mark.parametrize(
    ("initial_radius", "final_radius", "inclination_change"),
    [
        (float("nan"), 7_171_000, 10),
        (6_771_000, float("inf"), 10),
        (6_771_000, 7_171_000, float("nan")),
        (True, 7_171_000, 10),
    ],
)
def test_non_finite_or_boolean_inputs_are_rejected(
    initial_radius,
    final_radius,
    inclination_change,
):
    with pytest.raises(ValueError):
        analyze_advanced_mission(
            initial_radius,
            final_radius,
            inclination_change,
        )
