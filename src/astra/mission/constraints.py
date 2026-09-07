"""Mission feasibility and constraint analysis for ASTRA."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MissionConstraints:
    """Physical constraints available to a spacecraft."""

    dry_mass: float
    propellant_mass: float
    specific_impulse: float
    maximum_delta_v: float


@dataclass(frozen=True)
class FeasibilityResult:
    """Result of checking mission feasibility."""

    required_delta_v: float
    available_delta_v: float
    delta_v_margin: float
    feasible: bool


def evaluate_delta_v_feasibility(
    required_delta_v: float,
    available_delta_v: float,
) -> FeasibilityResult:
    """Determine whether available delta-v can satisfy a mission."""

    if required_delta_v < 0:
        raise ValueError(
            "Required delta-v cannot be negative."
        )

    if available_delta_v < 0:
        raise ValueError(
            "Available delta-v cannot be negative."
        )

    margin = available_delta_v - required_delta_v

    return FeasibilityResult(
        required_delta_v=required_delta_v,
        available_delta_v=available_delta_v,
        delta_v_margin=margin,
        feasible=margin >= 0,
    )