"""Propellant-constrained mission analysis for ASTRA."""

from dataclasses import dataclass
import math

from astra.physics.rocket import propellant_mass_for_delta_v


@dataclass(frozen=True)
class PropellantFeasibility:
    """Result of checking whether a spacecraft has enough propellant."""

    initial_mass: float
    dry_mass: float
    propellant_available: float
    propellant_required: float
    propellant_remaining: float
    required_delta_v: float
    feasible: bool


def evaluate_propellant_feasibility(
    dry_mass: float,
    propellant_available: float,
    specific_impulse: float,
    required_delta_v: float,
) -> PropellantFeasibility:
    """Determine whether available propellant can perform a mission."""

    if dry_mass <= 0:
        raise ValueError(
            "Dry mass must be greater than zero."
        )

    if propellant_available < 0:
        raise ValueError(
            "Available propellant cannot be negative."
        )

    if specific_impulse <= 0:
        raise ValueError(
            "Specific impulse must be greater than zero."
        )

    if required_delta_v < 0:
        raise ValueError(
            "Required delta-v cannot be negative."
        )

    initial_mass = dry_mass + propellant_available

    propellant_required = propellant_mass_for_delta_v(
        initial_mass=initial_mass,
        delta_v=required_delta_v,
        specific_impulse=specific_impulse,
    )

    propellant_remaining = (
        propellant_available - propellant_required
    )

    return PropellantFeasibility(
        initial_mass=initial_mass,
        dry_mass=dry_mass,
        propellant_available=propellant_available,
        propellant_required=propellant_required,
        propellant_remaining=propellant_remaining,
        required_delta_v=required_delta_v,
        feasible=propellant_remaining >= 0,
    )