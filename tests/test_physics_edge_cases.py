"""Regression tests for invalid numerical inputs in ASTRA."""

import math

import pytest

from astra.physics.orbital import (
    circular_orbital_velocity,
    escape_velocity,
    orbital_period,
    specific_orbital_energy,
)
from astra.physics.transfers import hohmann_transfer
from astra.validation.high_fidelity_validation import (
    compare_value,
    validate_trajectory,
)


@pytest.mark.parametrize(
    "function",
    [
        circular_orbital_velocity,
        escape_velocity,
        orbital_period,
        specific_orbital_energy,
    ],
)
@pytest.mark.parametrize("radius", [math.nan, math.inf])
def test_orbital_functions_reject_non_finite_radii(function, radius):
    with pytest.raises(ValueError):
        function(radius)


@pytest.mark.parametrize(
    ("initial_radius", "final_radius"),
    [
        (math.nan, 7_000_000.0),
        (math.inf, 7_000_000.0),
        (7_000_000.0, math.nan),
        (7_000_000.0, math.inf),
    ],
)
def test_hohmann_transfer_rejects_non_finite_radii(
    initial_radius,
    final_radius,
):
    with pytest.raises(ValueError):
        hohmann_transfer(initial_radius, final_radius)


@pytest.mark.parametrize("tolerance", [math.nan, math.inf, -math.inf, -1.0])
def test_compare_value_rejects_invalid_tolerance(tolerance):
    with pytest.raises(ValueError):
        compare_value(
            name="test metric",
            expected=10.0,
            actual=10.0,
            tolerance=tolerance,
        )


@pytest.mark.parametrize(
    "positions",
    [
        [(math.nan, 0.0, 0.0)],
        [(0.0, math.inf, 0.0)],
        [(0.0, 0.0, -math.inf)],
    ],
)
def test_trajectory_validator_rejects_non_finite_coordinates(positions):
    with pytest.raises(ValueError):
        validate_trajectory(
            expected_positions=[(1.0, 2.0, 3.0)],
            actual_positions=positions,
            position_tolerance=1.0,
        )


@pytest.mark.parametrize("tolerance", [math.nan, math.inf, -math.inf, -1.0])
def test_trajectory_validator_rejects_invalid_tolerance(tolerance):
    with pytest.raises(ValueError):
        validate_trajectory(
            expected_positions=[(1.0, 2.0, 3.0)],
            actual_positions=[(1.0, 2.0, 3.0)],
            position_tolerance=tolerance,
        )