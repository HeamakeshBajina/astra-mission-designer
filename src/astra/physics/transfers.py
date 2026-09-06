"""Orbital transfer calculations for ASTRA."""

import math
from dataclasses import dataclass

from .constants import EARTH_MU


@dataclass(frozen=True)
class HohmannTransfer:
    """Results from a Hohmann transfer between two circular orbits."""

    initial_radius: float
    final_radius: float
    transfer_semi_major_axis: float
    first_burn_delta_v: float
    second_burn_delta_v: float
    total_delta_v: float
    transfer_time: float


def hohmann_transfer(
    initial_radius: float,
    final_radius: float,
) -> HohmannTransfer:
    """Calculate a Hohmann transfer between two circular Earth orbits.

    Parameters
    ----------
    initial_radius : float
        Radius of the initial circular orbit from Earth's center, in metres.

    final_radius : float
        Radius of the final circular orbit from Earth's center, in metres.

    Returns
    -------
    HohmannTransfer
        Calculated transfer-orbit and mission Δv results.

    Raises
    ------
    ValueError
        If either radius is not positive or the two radii are equal.
    """
    if initial_radius <= 0 or final_radius <= 0:
        raise ValueError("Orbit radii must be greater than zero.")

    if math.isclose(initial_radius, final_radius):
        raise ValueError("Initial and final orbit radii must be different.")

    # Semi-major axis of the elliptical transfer orbit.
    transfer_a = (initial_radius + final_radius) / 2

    # Circular velocity at each orbit.
    initial_velocity = math.sqrt(EARTH_MU / initial_radius)
    final_velocity = math.sqrt(EARTH_MU / final_radius)

    # Velocity at periapsis and apoapsis of the transfer ellipse.
    transfer_periapsis_velocity = math.sqrt(
        EARTH_MU
        * (2 / initial_radius - 1 / transfer_a)
    )

    transfer_apoapsis_velocity = math.sqrt(
        EARTH_MU
        * (2 / final_radius - 1 / transfer_a)
    )

    # Magnitude of the two burns.
    first_burn_delta_v = abs(
        transfer_periapsis_velocity - initial_velocity
    )

    second_burn_delta_v = abs(
        final_velocity - transfer_apoapsis_velocity
    )

    total_delta_v = first_burn_delta_v + second_burn_delta_v

    # Hohmann transfer takes half the period of the transfer ellipse.
    transfer_time = math.pi * math.sqrt(
        transfer_a**3 / EARTH_MU
    )

    return HohmannTransfer(
        initial_radius=initial_radius,
        final_radius=final_radius,
        transfer_semi_major_axis=transfer_a,
        first_burn_delta_v=first_burn_delta_v,
        second_burn_delta_v=second_burn_delta_v,
        total_delta_v=total_delta_v,
        transfer_time=transfer_time,
    )