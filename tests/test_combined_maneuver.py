"""Tests for combined orbital maneuver calculations."""

import pytest

from astra.physics.combined_maneuver import (
    combined_delta_v,
    combined_orbital_plane_change,
)


def test_zero_components_require_zero_delta_v():
    assert combined_delta_v(0, 0) == pytest.approx(0.0)


def test_perpendicular_delta_v_vectors_use_pythagorean_sum():
    result = combined_delta_v(
        orbital_delta_v=300,
        plane_change_delta_v_value=400,
        angle_between_burns=90,
    )

    assert result == pytest.approx(500.0)


def test_parallel_delta_v_vectors_add():
    result = combined_delta_v(
        orbital_delta_v=300,
        plane_change_delta_v_value=400,
        angle_between_burns=0,
    )

    assert result == pytest.approx(700.0)


def test_opposite_delta_v_vectors_subtract():
    result = combined_delta_v(
        orbital_delta_v=400,
        plane_change_delta_v_value=300,
        angle_between_burns=180,
    )

    assert result == pytest.approx(100.0)


def test_negative_orbital_delta_v_is_rejected():
    with pytest.raises(ValueError):
        combined_delta_v(-1, 100)


def test_negative_plane_change_delta_v_is_rejected():
    with pytest.raises(ValueError):
        combined_delta_v(100, -1)


def test_invalid_angle_is_rejected():
    with pytest.raises(ValueError):
        combined_delta_v(100, 100, 181)


def test_combined_orbital_plane_change_returns_components():
    result = combined_orbital_plane_change(
        orbital_delta_v=500,
        radius=7_000_000,
        inclination_change=10,
    )

    assert result.orbital_delta_v == pytest.approx(500)
    assert result.plane_change_delta_v > 0
    assert result.combined_delta_v > result.orbital_delta_v