"""Atmospheric density and drag models for ASTRA."""

from dataclasses import dataclass
import math

from astra.physics.constants import EARTH_RADIUS


@dataclass(frozen=True)
class AtmosphericModel:
    """Simple exponential atmosphere model for Earth."""

    reference_density: float = 1.225
    reference_altitude: float = 0.0
    scale_height: float = 8500.0
    minimum_altitude: float = 0.0
    maximum_altitude: float = 1_000_000.0

    def __post_init__(self) -> None:
        """Validate atmospheric model parameters."""

        if self.reference_density <= 0:
            raise ValueError(
                "Reference density must be greater than zero."
            )

        if self.scale_height <= 0:
            raise ValueError(
                "Scale height must be greater than zero."
            )

        if self.maximum_altitude <= self.minimum_altitude:
            raise ValueError(
                "Maximum altitude must be greater than minimum altitude."
            )

        if self.reference_altitude < self.minimum_altitude:
            raise ValueError(
                "Reference altitude cannot be below minimum altitude."
            )

        if self.reference_altitude > self.maximum_altitude:
            raise ValueError(
                "Reference altitude cannot exceed maximum altitude."
            )

    def density(self, altitude: float) -> float:
        """Return atmospheric density in kg/m^3.

        Uses an exponential density model:

            rho = rho_ref * exp(-(h - h_ref) / H)

        The density is treated as zero outside the configured
        atmospheric validity range.
        """

        if altitude < 0:
            raise ValueError(
                "Altitude cannot be negative."
            )

        if altitude > self.maximum_altitude:
            return 0.0

        if altitude < self.minimum_altitude:
            return 0.0

        exponent = -(
            altitude - self.reference_altitude
        ) / self.scale_height

        return self.reference_density * math.exp(exponent)

    def density_at_radius(self, radius: float) -> float:
        """Return atmospheric density from geocentric radius."""

        if radius <= 0:
            raise ValueError(
                "Radius must be greater than zero."
            )

        altitude = radius - EARTH_RADIUS

        if altitude < 0:
            raise ValueError(
                "Radius cannot be below Earth's surface."
            )

        return self.density(altitude)


@dataclass(frozen=True)
class DragModel:
    """Spacecraft aerodynamic drag parameters."""

    drag_coefficient: float
    reference_area: float

    def __post_init__(self) -> None:
        """Validate drag parameters."""

        if self.drag_coefficient < 0:
            raise ValueError(
                "Drag coefficient cannot be negative."
            )

        if self.reference_area < 0:
            raise ValueError(
                "Reference area cannot be negative."
            )


def atmospheric_rotation_velocity(
    position: tuple[float, float, float],
    angular_velocity: float = 7.2921150e-5,
) -> tuple[float, float, float]:
    """Return atmospheric co-rotation velocity in m/s.

    Earth is approximated as rotating about the +Z axis.
    """

    if angular_velocity < 0:
        raise ValueError(
            "Angular velocity cannot be negative."
        )

    x, y, _ = position

    return (
        -angular_velocity * y,
        angular_velocity * x,
        0.0,
    )


def relative_atmospheric_velocity(
    velocity: tuple[float, float, float],
    position: tuple[float, float, float],
    angular_velocity: float = 7.2921150e-5,
) -> tuple[float, float, float]:
    """Return spacecraft velocity relative to rotating atmosphere."""

    atmospheric_velocity = atmospheric_rotation_velocity(
        position=position,
        angular_velocity=angular_velocity,
    )

    return (
        velocity[0] - atmospheric_velocity[0],
        velocity[1] - atmospheric_velocity[1],
        velocity[2] - atmospheric_velocity[2],
    )


def drag_acceleration(
    position: tuple[float, float, float],
    velocity: tuple[float, float, float],
    mass: float,
    drag_model: DragModel,
    atmospheric_model: AtmosphericModel | None = None,
    earth_rotation_rate: float = 7.2921150e-5,
) -> tuple[float, float, float]:
    """Return atmospheric drag acceleration in m/s^2."""

    if mass <= 0:
        raise ValueError(
            "Mass must be greater than zero."
        )

    if atmospheric_model is None:
        atmospheric_model = AtmosphericModel()

    radius = math.sqrt(
        position[0] ** 2
        + position[1] ** 2
        + position[2] ** 2
    )

    altitude = radius - EARTH_RADIUS

    if altitude < 0:
        raise ValueError(
            "Spacecraft position cannot be below Earth's surface."
        )

    density = atmospheric_model.density(
        altitude
    )

    if density == 0.0:
        return (0.0, 0.0, 0.0)

    relative_velocity = relative_atmospheric_velocity(
        velocity=velocity,
        position=position,
        angular_velocity=earth_rotation_rate,
    )

    speed = math.sqrt(
        relative_velocity[0] ** 2
        + relative_velocity[1] ** 2
        + relative_velocity[2] ** 2
    )

    if speed == 0.0:
        return (0.0, 0.0, 0.0)

    coefficient = (
        -0.5
        * density
        * drag_model.drag_coefficient
        * drag_model.reference_area
        / mass
        * speed
    )

    return (
        coefficient * relative_velocity[0],
        coefficient * relative_velocity[1],
        coefficient * relative_velocity[2],
    )
