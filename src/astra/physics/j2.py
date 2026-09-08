"""Earth J2 oblateness perturbation model for ASTRA."""

import math

from .constants import EARTH_MU


# Earth's second zonal harmonic coefficient.
EARTH_J2 = 1.08262668e-3


def j2_acceleration(
    x: float,
    y: float,
    z: float,
) -> tuple[float, float, float]:
    """Calculate acceleration caused by Earth's J2 oblateness.

    Parameters
    ----------
    x, y, z:
        Spacecraft position in metres in an Earth-centered
        inertial Cartesian coordinate system.

    Returns
    -------
    tuple[float, float, float]
        J2 perturbation acceleration in m/s².
    """

    radius_squared = x**2 + y**2 + z**2

    if radius_squared <= 0:
        raise ValueError(
            "Position cannot be at Earth's center."
        )

    radius = math.sqrt(radius_squared)
    radius_five = radius**5

    factor = (
        1.5
        * EARTH_J2
        * EARTH_MU
        / radius_five
    )

    z_ratio_squared = (z / radius) ** 2

    ax = factor * x * (
        5 * z_ratio_squared - 1
    )

    ay = factor * y * (
        5 * z_ratio_squared - 1
    )

    az = factor * z * (
        5 * z_ratio_squared - 3
    )

    return ax, ay, az