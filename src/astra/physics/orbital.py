"""Basic orbital mechanics calculations for ASTRA."""

import math

from .constants import EARTH_MU


def circular_orbital_velocity(radius: float) -> float:
    """Return circular orbital velocity at a given radius.

    Parameters
    ----------
    radius : float
        Distance from Earth's center in metres.

    Returns
    -------
    float
        Circular orbital velocity in metres per second.
    """
    if radius <= 0:
        raise ValueError("Radius must be greater than zero.")

    return math.sqrt(EARTH_MU / radius)


def escape_velocity(radius: float) -> float:
    """Return escape velocity at a given radius in metres per second."""
    if radius <= 0:
        raise ValueError("Radius must be greater than zero.")

    return math.sqrt(2 * EARTH_MU / radius)


def orbital_period(radius: float) -> float:
    """Return the period of a circular orbit in seconds."""
    if radius <= 0:
        raise ValueError("Radius must be greater than zero.")

    return 2 * math.pi * math.sqrt(radius**3 / EARTH_MU)


def specific_orbital_energy(radius: float) -> float:
    """Return specific orbital energy for a circular orbit.

    Returns
    -------
    float
        Specific orbital energy in J/kg.
    """
    if radius <= 0:
        raise ValueError("Radius must be greater than zero.")

    return -EARTH_MU / (2 * radius)