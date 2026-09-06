import pytest

from astra.physics.constants import EARTH_RADIUS
from astra.simulation.validation import validate_hohmann_transfer


INITIAL_RADIUS = EARTH_RADIUS + 400_000
FINAL_RADIUS = EARTH_RADIUS + 800_000


def test_numerical_transfer_has_small_radius_error():
    result = validate_hohmann_transfer(
        INITIAL_RADIUS,
        FINAL_RADIUS,
        dt=10,
    )

    assert result.radius_error_percent < 0.01


def test_numerical_transfer_has_small_velocity_error():
    result = validate_hohmann_transfer(
        INITIAL_RADIUS,
        FINAL_RADIUS,
        dt=10,
    )

    assert result.velocity_error_percent < 0.01


def test_smaller_timestep_reduces_radius_error():
    coarse = validate_hohmann_transfer(
        INITIAL_RADIUS,
        FINAL_RADIUS,
        dt=60,
    )

    fine = validate_hohmann_transfer(
        INITIAL_RADIUS,
        FINAL_RADIUS,
        dt=10,
    )

    assert fine.radius_error <= coarse.radius_error


def test_smaller_timestep_reduces_velocity_error():
    coarse = validate_hohmann_transfer(
        INITIAL_RADIUS,
        FINAL_RADIUS,
        dt=60,
    )

    fine = validate_hohmann_transfer(
        INITIAL_RADIUS,
        FINAL_RADIUS,
        dt=10,
    )

    assert fine.velocity_error <= coarse.velocity_error


def test_lowering_transfer_is_validated():
    result = validate_hohmann_transfer(
        FINAL_RADIUS,
        INITIAL_RADIUS,
        dt=10,
    )

    assert result.radius_error_percent < 0.01
    assert result.velocity_error_percent < 0.01


@pytest.mark.parametrize(
    "dt",
    [60, 30, 10, 5],
)
def test_multiple_timesteps_produce_valid_results(dt):
    result = validate_hohmann_transfer(
        INITIAL_RADIUS,
        FINAL_RADIUS,
        dt=dt,
    )

    assert result.radius_error_percent < 1.0
    assert result.velocity_error_percent < 1.0