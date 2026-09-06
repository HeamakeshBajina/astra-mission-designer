"""Numerical validation utilities for ASTRA."""

from dataclasses import dataclass
import math

from astra.physics.constants import EARTH_MU
from astra.physics.transfers import hohmann_transfer
from astra.simulation.mission_trajectory import (
    simulate_continuous_hohmann,
)


@dataclass(frozen=True)
class TransferValidation:
    """Numerical error between analytical and simulated transfer results."""

    timestep: float
    radius_error: float
    radius_error_percent: float
    velocity_error: float
    velocity_error_percent: float


def validate_hohmann_transfer(
    initial_radius: float,
    final_radius: float,
    dt: float,
) -> TransferValidation:
    """Compare numerical Hohmann transfer results with analytical values."""

    if initial_radius <= 0:
        raise ValueError(
            "Initial radius must be greater than zero."
        )

    if final_radius <= 0:
        raise ValueError(
            "Final radius must be greater than zero."
        )

    if math.isclose(initial_radius, final_radius):
        raise ValueError(
            "Initial and final orbit radii must be different."
        )

    if dt <= 0:
        raise ValueError(
            "Timestep must be greater than zero."
        )

    analytical = hohmann_transfer(
        initial_radius,
        final_radius,
    )

    numerical = simulate_continuous_hohmann(
        initial_radius,
        final_radius,
        dt=dt,
    )

    transfer_endpoint = numerical.burns[1].state_before

    numerical_radius = math.hypot(
        transfer_endpoint.x,
        transfer_endpoint.y,
    )

    numerical_speed = math.hypot(
        transfer_endpoint.vx,
        transfer_endpoint.vy,
    )

    transfer_radius_error = abs(
        numerical_radius - final_radius
    )

    transfer_radius_error_percent = (
        transfer_radius_error
        / final_radius
        * 100
    )

    if final_radius > initial_radius:
        expected_transfer_speed = math.sqrt(
            EARTH_MU
            * (
                2 / final_radius
                - 1 / analytical.transfer_semi_major_axis
            )
        )
    else:
        expected_transfer_speed = math.sqrt(
            EARTH_MU
            * (
                2 / final_radius
                - 1 / analytical.transfer_semi_major_axis
            )
        )

    transfer_velocity_error = abs(
        numerical_speed - expected_transfer_speed
    )

    transfer_velocity_error_percent = (
        transfer_velocity_error
        / expected_transfer_speed
        * 100
    )

    return TransferValidation(
        timestep=dt,
        radius_error=transfer_radius_error,
        radius_error_percent=transfer_radius_error_percent,
        velocity_error=transfer_velocity_error,
        velocity_error_percent=transfer_velocity_error_percent,
    )