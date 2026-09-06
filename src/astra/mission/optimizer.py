"""Orbital transfer strategy optimization for ASTRA."""

from dataclasses import dataclass
import math

from astra.physics.constants import EARTH_MU, EARTH_RADIUS
from astra.physics.rocket import propellant_mass_for_delta_v
from astra.physics.transfers import hohmann_transfer


@dataclass(frozen=True)
class TransferCandidate:
    """One evaluated orbital transfer strategy."""

    strategy: str
    intermediate_altitude: float | None
    total_delta_v: float
    required_propellant: float
    feasible: bool


@dataclass(frozen=True)
class OptimizationResult:
    """Result of comparing multiple orbital transfer strategies."""

    best_candidate: TransferCandidate
    candidates: list[TransferCandidate]


def _circular_velocity(radius: float) -> float:
    """Return circular orbital velocity."""

    return math.sqrt(EARTH_MU / radius)


def _transfer_velocity(
    radius: float,
    semi_major_axis: float,
) -> float:
    """Return orbital velocity using the vis-viva equation."""

    return math.sqrt(
        EARTH_MU
        * (
            2 / radius
            - 1 / semi_major_axis
        )
    )


def _bielliptic_delta_v(
    initial_radius: float,
    final_radius: float,
    intermediate_radius: float,
) -> float:
    """Calculate total Δv for a three-burn bi-elliptic transfer."""

    if intermediate_radius <= max(
        initial_radius,
        final_radius,
    ):
        raise ValueError(
            "Intermediate radius must be greater than "
            "both endpoint radii."
        )

    first_semi_major_axis = (
        initial_radius + intermediate_radius
    ) / 2

    second_semi_major_axis = (
        final_radius + intermediate_radius
    ) / 2

    initial_circular_velocity = _circular_velocity(
        initial_radius
    )

    final_circular_velocity = _circular_velocity(
        final_radius
    )

    first_transfer_velocity = _transfer_velocity(
        initial_radius,
        first_semi_major_axis,
    )

    first_apoapsis_velocity = _transfer_velocity(
        intermediate_radius,
        first_semi_major_axis,
    )

    second_apoapsis_velocity = _transfer_velocity(
        intermediate_radius,
        second_semi_major_axis,
    )

    second_periapsis_velocity = _transfer_velocity(
        final_radius,
        second_semi_major_axis,
    )

    first_burn = abs(
        first_transfer_velocity
        - initial_circular_velocity
    )

    second_burn = abs(
        second_apoapsis_velocity
        - first_apoapsis_velocity
    )

    third_burn = abs(
        final_circular_velocity
        - second_periapsis_velocity
    )

    return (
        first_burn
        + second_burn
        + third_burn
    )


def optimize_transfer_strategy(
    initial_altitude: float,
    final_altitude: float,
    spacecraft_mass: float,
    specific_impulse: float,
    available_propellant: float,
    minimum_intermediate_altitude: float,
    maximum_intermediate_altitude: float,
    step: float,
) -> OptimizationResult:
    """Search Hohmann and bi-elliptic transfer strategies."""

    if initial_altitude < 0:
        raise ValueError(
            "Initial altitude cannot be negative."
        )

    if final_altitude < 0:
        raise ValueError(
            "Final altitude cannot be negative."
        )

    if final_altitude <= initial_altitude:
        raise ValueError(
            "The optimizer currently supports "
            "raising transfers only."
        )

    if spacecraft_mass <= 0:
        raise ValueError(
            "Spacecraft mass must be greater than zero."
        )

    if specific_impulse <= 0:
        raise ValueError(
            "Specific impulse must be greater than zero."
        )

    if available_propellant < 0:
        raise ValueError(
            "Available propellant cannot be negative."
        )

    if minimum_intermediate_altitude <= final_altitude:
        raise ValueError(
            "Minimum intermediate altitude must be "
            "greater than the target altitude."
        )

    if maximum_intermediate_altitude <= (
        minimum_intermediate_altitude
    ):
        raise ValueError(
            "Maximum intermediate altitude must be "
            "greater than minimum intermediate altitude."
        )

    if step <= 0:
        raise ValueError(
            "Optimization step must be greater than zero."
        )

    initial_radius = (
        EARTH_RADIUS + initial_altitude
    )

    final_radius = (
        EARTH_RADIUS + final_altitude
    )

    candidates = []

    # -----------------------------------------------------
    # Baseline Hohmann transfer
    # -----------------------------------------------------

    hohmann = hohmann_transfer(
        initial_radius,
        final_radius,
    )

    hohmann_propellant = propellant_mass_for_delta_v(
        initial_mass=spacecraft_mass,
        delta_v=hohmann.total_delta_v,
        specific_impulse=specific_impulse,
    )

    candidates.append(
        TransferCandidate(
            strategy="Hohmann",
            intermediate_altitude=None,
            total_delta_v=hohmann.total_delta_v,
            required_propellant=hohmann_propellant,
            feasible=(
                hohmann_propellant
                <= available_propellant
            ),
        )
    )

    # -----------------------------------------------------
    # Bi-elliptic transfer search
    # -----------------------------------------------------

    intermediate_altitude = (
        minimum_intermediate_altitude
    )

    while (
        intermediate_altitude
        <= maximum_intermediate_altitude + 1e-9
    ):
        intermediate_radius = (
            EARTH_RADIUS
            + intermediate_altitude
        )

        total_delta_v = _bielliptic_delta_v(
            initial_radius=initial_radius,
            final_radius=final_radius,
            intermediate_radius=intermediate_radius,
        )

        required_propellant = (
            propellant_mass_for_delta_v(
                initial_mass=spacecraft_mass,
                delta_v=total_delta_v,
                specific_impulse=specific_impulse,
            )
        )

        candidates.append(
            TransferCandidate(
                strategy="Bi-elliptic",
                intermediate_altitude=(
                    intermediate_altitude
                ),
                total_delta_v=total_delta_v,
                required_propellant=required_propellant,
                feasible=(
                    required_propellant
                    <= available_propellant
                ),
            )
        )

        intermediate_altitude += step

    feasible_candidates = [
        candidate
        for candidate in candidates
        if candidate.feasible
    ]

    if not feasible_candidates:
        raise ValueError(
            "No feasible transfer strategy was found."
        )

    best_candidate = min(
        feasible_candidates,
        key=lambda candidate: candidate.total_delta_v,
    )

    return OptimizationResult(
        best_candidate=best_candidate,
        candidates=candidates,
    )