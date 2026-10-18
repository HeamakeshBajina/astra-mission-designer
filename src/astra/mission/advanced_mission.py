"""Advanced mission analysis for ASTRA.

Models a circular-to-circular Hohmann transfer with an optional
inclination change performed during the arrival burn at the target orbit.
"""

import math
from dataclasses import dataclass

from astra.physics.constants import EARTH_MU
from astra.physics.transfers import hohmann_transfer


@dataclass(frozen=True)
class AdvancedMission:
    """Results for a Hohmann transfer with a plane change at arrival.

    Radii are in metres, delta-v values in metres per second,
    transfer time in seconds, and inclination change in degrees.
    """

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
    """Analyze a Hohmann transfer with a plane change at arrival.

    The first Hohmann burn is unchanged. The arrival burn combines
    circularization and inclination change using the actual transfer
    apoapsis and target circular-orbit velocity magnitudes.
    """
    for name, value in (
        ("Initial radius", initial_radius),
        ("Final radius", final_radius),
        ("Inclination change", inclination_change),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a finite number.")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")

    if initial_radius <= 0:
        raise ValueError("Initial radius must be greater than zero.")
    if final_radius <= 0:
        raise ValueError("Final radius must be greater than zero.")
    if not 0 <= inclination_change <= 180:
        raise ValueError(
            "Inclination change must be between 0 and 180 degrees."
        )

    transfer = hohmann_transfer(initial_radius, final_radius)

    transfer_arrival_velocity = math.sqrt(
        EARTH_MU
        * (
            2 / final_radius
            - 1 / transfer.transfer_semi_major_axis
        )
    )
    target_circular_velocity = math.sqrt(EARTH_MU / final_radius)
    angle = math.radians(inclination_change)

    arrival_burn_delta_v = math.sqrt(
        transfer_arrival_velocity**2
        + target_circular_velocity**2
        - 2
        * transfer_arrival_velocity
        * target_circular_velocity
        * math.cos(angle)
    )

    plane_change_delta_v = (
        2
        * target_circular_velocity
        * math.sin(angle / 2)
    )

    total_delta_v = (
        transfer.first_burn_delta_v + arrival_burn_delta_v
    )

    return AdvancedMission(
        initial_radius=initial_radius,
        final_radius=final_radius,
        inclination_change=inclination_change,
        hohmann_delta_v=transfer.total_delta_v,
        plane_change_delta_v=plane_change_delta_v,
        combined_delta_v=total_delta_v,
        transfer_time=transfer.transfer_time,
    )
