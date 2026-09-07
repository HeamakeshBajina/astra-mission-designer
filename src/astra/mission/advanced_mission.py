"""Advanced mission analysis for ASTRA."""

from dataclasses import dataclass

from astra.physics.combined_maneuver import (
    combined_orbital_plane_change,
)
from astra.physics.transfers import hohmann_transfer


@dataclass(frozen=True)
class AdvancedMission:
    """Mission analysis combining orbital transfer and plane change."""

    initial_radius: float
    final_radius: float
    inclination_change: float
    hohmann_delta_v: float
    plane_change_delta_v: float
    combined_delta_v: float
    transfer_time: float


def analyze_advanced_mission(
    initial_radius: float,
    final_radius: float,
    inclination_change: float,
) -> AdvancedMission:
    """Analyze an orbital transfer with an inclination change."""
    if initial_radius <= 0:
        raise ValueError(
            "Initial radius must be greater than zero."
        )

    if final_radius <= 0:
        raise ValueError(
            "Final radius must be greater than zero."
        )

    if inclination_change < 0:
        raise ValueError(
            "Inclination change cannot be negative."
        )

    transfer = hohmann_transfer(
        initial_radius,
        final_radius,
    )

    maneuver = combined_orbital_plane_change(
        orbital_delta_v=transfer.total_delta_v,
        radius=final_radius,
        inclination_change=inclination_change,
    )

    return AdvancedMission(
        initial_radius=initial_radius,
        final_radius=final_radius,
        inclination_change=inclination_change,
        hohmann_delta_v=transfer.total_delta_v,
        plane_change_delta_v=maneuver.plane_change_delta_v,
        combined_delta_v=maneuver.combined_delta_v,
        transfer_time=transfer.transfer_time,
    )