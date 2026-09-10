"""Solar radiation pressure models for ASTRA."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SolarRadiationPressureModel:
    """Spacecraft solar radiation pressure parameters."""

    solar_pressure: float = 4.56e-6
    reflectivity_coefficient: float = 1.0
    reference_area: float = 0.0
    reference_distance: float = 149_597_870_700.0

    def __post_init__(self) -> None:
        """Validate solar radiation pressure parameters."""

        if self.solar_pressure < 0:
            raise ValueError(
                "Solar pressure cannot be negative."
            )

        if self.reflectivity_coefficient < 0:
            raise ValueError(
                "Reflectivity coefficient cannot be negative."
            )

        if self.reference_area < 0:
            raise ValueError(
                "Reference area cannot be negative."
            )

        if self.reference_distance <= 0:
            raise ValueError(
                "Reference distance must be greater than zero."
            )


def sun_distance_scaling(
    distance_from_sun: float,
    reference_distance: float = 149_597_870_700.0,
) -> float:
    """Return inverse-square solar-pressure scaling."""

    if distance_from_sun <= 0:
        raise ValueError(
            "Distance from Sun must be greater than zero."
        )

    if reference_distance <= 0:
        raise ValueError(
            "Reference distance must be greater than zero."
        )

    return (
        reference_distance / distance_from_sun
    ) ** 2


def solar_pressure_at_distance(
    distance_from_sun: float,
    solar_pressure_at_reference: float = 4.56e-6,
    reference_distance: float = 149_597_870_700.0,
) -> float:
    """Return solar radiation pressure at a given Sun distance."""

    if solar_pressure_at_reference < 0:
        raise ValueError(
            "Reference solar pressure cannot be negative."
        )

    return (
        solar_pressure_at_reference
        * sun_distance_scaling(
            distance_from_sun=distance_from_sun,
            reference_distance=reference_distance,
        )
    )


def srp_acceleration(
    position: tuple[float, float, float],
    mass: float,
    model: SolarRadiationPressureModel,
    sun_direction: tuple[float, float, float],
    distance_from_sun: float | None = None,
) -> tuple[float, float, float]:
    """Return solar radiation pressure acceleration in m/s^2.

    ``sun_direction`` points from the spacecraft toward the Sun.
    The resulting acceleration therefore points in the opposite
    direction because radiation pressure pushes the spacecraft away
    from the Sun.
    """

    if mass <= 0:
        raise ValueError(
            "Mass must be greater than zero."
        )

    magnitude = math.sqrt(
        sun_direction[0] ** 2
        + sun_direction[1] ** 2
        + sun_direction[2] ** 2
    )

    if magnitude <= 0:
        raise ValueError(
            "Sun direction cannot be the zero vector."
        )

    if model.reference_area == 0.0:
        return (0.0, 0.0, 0.0)

    if distance_from_sun is None:
        distance_from_sun = model.reference_distance

    pressure = solar_pressure_at_distance(
        distance_from_sun=distance_from_sun,
        solar_pressure_at_reference=model.solar_pressure,
        reference_distance=model.reference_distance,
    )

    scale = (
        -pressure
        * model.reflectivity_coefficient
        * model.reference_area
        / mass
        / magnitude
    )

    return (
        scale * sun_direction[0],
        scale * sun_direction[1],
        scale * sun_direction[2],
    )
