"""Orbital plane-change calculations for ASTRA."""

import math

from .constants import EARTH_MU


def plane_change_delta_v(
    radius: float,
    inclination_change: float,
) -> float:
    """Return the ideal instantaneous plane-change delta-v.

    Parameters
    ----------
    radius:
        Orbital radius in metres.

    inclination_change:
        Change in orbital inclination in degrees.

    Returns
    -------
    float
        Required delta-v in metres per second.

    Notes
    -----
    This model assumes an instantaneous pure plane change
    performed at a point where the spacecraft velocity is
    perpendicular to the orbital radius.
    """
    if radius <= 0:
        raise ValueError("Radius must be greater than zero.")

    if inclination_change < 0:
        raise ValueError(
            "Inclination change cannot be negative."
        )

    if inclination_change > 180:
        raise ValueError(
            "Inclination change cannot exceed 180 degrees."
        )

    orbital_velocity = math.sqrt(EARTH_MU / radius)

    angle_radians = math.radians(inclination_change)

    return 2 * orbital_velocity * math.sin(
        angle_radians / 2
    )