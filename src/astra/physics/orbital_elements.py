"""Classical orbital-element calculations for ASTRA."""

from dataclasses import dataclass
import math

from astra.physics.constants import EARTH_MU
from astra.simulation.propagator_3d import State3D


@dataclass(frozen=True)
class OrbitalElements:
    """Classical orbital elements derived from a Cartesian state."""

    semi_major_axis: float
    eccentricity: float
    inclination: float
    raan: float
    argument_of_periapsis: float
    true_anomaly: float


def _dot(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> float:
    """Return the dot product of two vectors."""

    return sum(
        first[index] * second[index]
        for index in range(3)
    )


def _cross(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Return the cross product of two vectors."""

    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def _magnitude(
    vector: tuple[float, float, float],
) -> float:
    """Return the magnitude of a three-dimensional vector."""

    return math.sqrt(_dot(vector, vector))


def _clamp(value: float) -> float:
    """Clamp a floating-point value into [-1, 1]."""

    return max(-1.0, min(1.0, value))


def _normalize_angle(angle: float) -> float:
    """Normalize an angle in degrees into [0, 360)."""

    return angle % 360.0


def orbital_elements_from_state(
    state: State3D,
) -> OrbitalElements:
    """Convert a Cartesian state into classical orbital elements.

    Position is in metres and velocity is in metres per second.

    Angular quantities are returned in degrees.
    """

    position = (
        state.x,
        state.y,
        state.z,
    )
    velocity = (
        state.vx,
        state.vy,
        state.vz,
    )

    radius = _magnitude(position)
    speed = _magnitude(velocity)

    if radius <= 0:
        raise ValueError(
            "Position cannot be at Earth's center."
        )

    angular_momentum = _cross(
        position,
        velocity,
    )
    h = _magnitude(angular_momentum)

    if h <= 0:
        raise ValueError(
            "Orbital angular momentum cannot be zero."
        )

    radial_velocity = _dot(
        position,
        velocity,
    )

    eccentricity_vector = tuple(
        (
            (
                (speed**2 - EARTH_MU / radius)
                * position[index]
                - radial_velocity * velocity[index]
            )
            / EARTH_MU
        )
        for index in range(3)
    )
    eccentricity = _magnitude(
        eccentricity_vector
    )

    specific_energy = (
        speed**2 / 2.0
        - EARTH_MU / radius
    )

    if abs(specific_energy) < 1e-15:
        semi_major_axis = math.inf
    else:
        semi_major_axis = (
            -EARTH_MU
            / (2.0 * specific_energy)
        )

    inclination = math.degrees(
        math.acos(
            _clamp(
                angular_momentum[2] / h
            )
        )
    )

    node_vector = (
        -angular_momentum[1],
        angular_momentum[0],
        0.0,
    )
    node_magnitude = _magnitude(
        node_vector
    )

    if node_magnitude > 1e-12:
        raan = _normalize_angle(
            math.degrees(
                math.atan2(
                    node_vector[1],
                    node_vector[0],
                )
            )
        )
    else:
        raan = 0.0

    if (
        eccentricity > 1e-12
        and node_magnitude > 1e-12
    ):
        argument_of_periapsis = _normalize_angle(
            math.degrees(
                math.atan2(
                    _dot(
                        _cross(
                            node_vector,
                            eccentricity_vector,
                        ),
                        angular_momentum,
                    ) / (
                        node_magnitude
                        * eccentricity
                        * h
                    ),
                    _dot(
                        node_vector,
                        eccentricity_vector,
                    ) / (
                        node_magnitude
                        * eccentricity
                    ),
                )
            )
        )
    else:
        argument_of_periapsis = 0.0

    if eccentricity > 1e-12:
        true_anomaly = _normalize_angle(
            math.degrees(
                math.atan2(
                    _dot(
                        _cross(
                            eccentricity_vector,
                            position,
                        ),
                        angular_momentum,
                    ) / (
                        eccentricity
                        * radius
                        * h
                    ),
                    _dot(
                        eccentricity_vector,
                        position,
                    ) / (
                        eccentricity
                        * radius
                    ),
                )
            )
        )
    else:
        if node_magnitude > 1e-12:
            true_anomaly = _normalize_angle(
                math.degrees(
                    math.atan2(
                        _dot(
                            _cross(
                                node_vector,
                                position,
                            ),
                            angular_momentum,
                        ) / (
                            node_magnitude
                            * radius
                            * h
                        ),
                        _dot(
                            node_vector,
                            position,
                        ) / (
                            node_magnitude
                            * radius
                        ),
                    )
                )
            )
        else:
            true_anomaly = _normalize_angle(
                math.degrees(
                    math.atan2(
                        position[1],
                        position[0],
                    )
                )
            )

    return OrbitalElements(
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        inclination=inclination,
        raan=raan,
        argument_of_periapsis=argument_of_periapsis,
        true_anomaly=true_anomaly,
    )
