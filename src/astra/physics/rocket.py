"""Rocket equation calculations for ASTRA."""

import math

from .constants import G0


def delta_v_from_mass_ratio(
    initial_mass: float,
    final_mass: float,
    specific_impulse: float,
) -> float:
    """Calculate available delta-v using the Tsiolkovsky rocket equation."""

    if initial_mass <= 0:
        raise ValueError("Initial mass must be greater than zero.")

    if final_mass <= 0:
        raise ValueError("Final mass must be greater than zero.")

    if final_mass >= initial_mass:
        raise ValueError("Final mass must be less than initial mass.")

    if specific_impulse <= 0:
        raise ValueError("Specific impulse must be greater than zero.")

    return (
        specific_impulse
        * G0
        * math.log(initial_mass / final_mass)
    )


def final_mass_for_delta_v(
    initial_mass: float,
    delta_v: float,
    specific_impulse: float,
) -> float:
    """Calculate final mass required for a given delta-v."""

    if initial_mass <= 0:
        raise ValueError("Initial mass must be greater than zero.")

    if delta_v < 0:
        raise ValueError("Delta-v cannot be negative.")

    if specific_impulse <= 0:
        raise ValueError("Specific impulse must be greater than zero.")

    return initial_mass / math.exp(
        delta_v / (specific_impulse * G0)
    )


def propellant_mass_for_delta_v(
    initial_mass: float,
    delta_v: float,
    specific_impulse: float,
) -> float:
    """Calculate propellant mass required for a given delta-v."""

    final_mass = final_mass_for_delta_v(
        initial_mass,
        delta_v,
        specific_impulse,
    )

    return initial_mass - final_mass