"""Thrust and burn-vector utilities for ASTRA."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class BurnVector:
    """A three-dimensional thrust-direction vector."""

    x: float
    y: float
    z: float

    @property
    def magnitude(self) -> float:
        """Return the vector magnitude."""
        return math.sqrt(
            self.x * self.x +
            self.y * self.y +
            self.z * self.z
        )

    @property
    def unit(self) -> tuple[float, float, float]:
        """Return the normalized vector."""
        magnitude = self.magnitude

        if magnitude <= 0:
            raise ValueError(
                "Burn vector cannot be the zero vector."
            )

        return (
            self.x / magnitude,
            self.y / magnitude,
            self.z / magnitude,
        )

    def scaled(self, factor: float) -> "BurnVector":
        """Return a vector scaled by a scalar factor."""
        return BurnVector(
            x=self.x * factor,
            y=self.y * factor,
            z=self.z * factor,
        )

    def __iter__(self):
        """Allow the vector to be unpacked as x, y, z."""
        return iter((self.x, self.y, self.z))


def normalize_vector(
    vector: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Normalize a three-dimensional vector."""
    return BurnVector(*vector).unit


def prograde_direction(
    velocity: tuple[float, float, float],
) -> BurnVector:
    """Return a burn vector aligned with spacecraft velocity."""
    return BurnVector(*velocity)


def retrograde_direction(
    velocity: tuple[float, float, float],
) -> BurnVector:
    """Return a burn vector opposite spacecraft velocity."""
    vector = BurnVector(*velocity)

    return BurnVector(
        x=-vector.x,
        y=-vector.y,
        z=-vector.z,
    )


def radial_out_direction(
    position: tuple[float, float, float],
) -> BurnVector:
    """Return a burn vector directed radially away from Earth."""
    return BurnVector(*position)


def radial_in_direction(
    position: tuple[float, float, float],
) -> BurnVector:
    """Return a burn vector directed radially toward Earth."""
    vector = BurnVector(*position)

    return BurnVector(
        x=-vector.x,
        y=-vector.y,
        z=-vector.z,
    )


def resolve_burn_direction(
    direction: BurnVector | tuple[float, float, float],
) -> tuple[float, float, float]:
    """Convert a burn direction into a normalized unit vector."""
    if isinstance(direction, BurnVector):
        return direction.unit

    return normalize_vector(direction)
