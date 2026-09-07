"""Combined orbital maneuver calculations for ASTRA."""

import math
from dataclasses import dataclass

from .plane_change import plane_change_delta_v


@dataclass(frozen=True)
class CombinedManeuver:
    """Results from combining an orbital burn with a plane change."""

    orbital_delta_v: float
    plane_change_delta_v: float
    combined_delta_v: float


def combined_delta_v(
    orbital_delta_v: float,
    plane_change_delta_v_value: float,
    angle_between_burns: float = 90.0,
) -> float:
    """Calculate the magnitude of two velocity changes performed together.

    Parameters
    ----------
    orbital_delta_v:
        Magnitude of the orbital velocity change in m/s.

    plane_change_delta_v_value:
        Magnitude of the plane-change velocity change in m/s.

    angle_between_burns:
        Angle between the two delta-v vectors in degrees.

    Returns
    -------
    float
        Combined delta-v magnitude in m/s.
    """
    if orbital_delta_v < 0:
        raise ValueError("Orbital delta-v cannot be negative.")

    if plane_change_delta_v_value < 0:
        raise ValueError(
            "Plane-change delta-v cannot be negative."
        )

    if not 0 <= angle_between_burns <= 180:
        raise ValueError(
            "Angle between burns must be between 0 and 180 degrees."
        )

    angle_radians = math.radians(angle_between_burns)

    return math.sqrt(
        orbital_delta_v**2
        + plane_change_delta_v_value**2
        + 2
        * orbital_delta_v
        * plane_change_delta_v_value
        * math.cos(angle_radians)
    )


def combined_orbital_plane_change(
    orbital_delta_v: float,
    radius: float,
    inclination_change: float,
    angle_between_burns: float = 90.0,
) -> CombinedManeuver:
    """Combine an orbital maneuver with an instantaneous plane change."""
    if orbital_delta_v < 0:
        raise ValueError("Orbital delta-v cannot be negative.")

    plane_change = plane_change_delta_v(
        radius,
        inclination_change,
    )

    total = combined_delta_v(
        orbital_delta_v,
        plane_change,
        angle_between_burns,
    )

    return CombinedManeuver(
        orbital_delta_v=orbital_delta_v,
        plane_change_delta_v=plane_change,
        combined_delta_v=total,
    )