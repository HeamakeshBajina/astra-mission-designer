"""3D orbital propagation with Earth's J2 perturbation for ASTRA."""

from dataclasses import dataclass
import math

from astra.physics.constants import EARTH_MU
from astra.physics.j2 import EARTH_J2


@dataclass(frozen=True)
class State3DJ2:
    """Spacecraft state for J2-perturbed 3D propagation."""

    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float


def total_acceleration_3d_j2(
    x: float,
    y: float,
    z: float,
) -> tuple[float, float, float]:
    """Calculate central-gravity plus J2 acceleration."""

    radius_squared = x**2 + y**2 + z**2

    if radius_squared <= 0:
        raise ValueError(
            "Position cannot be at Earth's center."
        )

    radius = math.sqrt(radius_squared)
    radius_cubed = radius**3

    # Central two-body gravitational acceleration.
    central_factor = -EARTH_MU / radius_cubed

    ax_central = central_factor * x
    ay_central = central_factor * y
    az_central = central_factor * z

    # Earth's J2 perturbation.
    z_ratio_squared = (z / radius) ** 2

    j2_factor = (
        1.5
        * EARTH_J2
        * EARTH_MU
        / radius_cubed
    )

    ax_j2 = (
        j2_factor
        * (x / radius**2)
        * (5 * z_ratio_squared - 1)
    )

    ay_j2 = (
        j2_factor
        * (y / radius**2)
        * (5 * z_ratio_squared - 1)
    )

    az_j2 = (
        j2_factor
        * (z / radius**2)
        * (5 * z_ratio_squared - 3)
    )

    return (
        ax_central + ax_j2,
        ay_central + ay_j2,
        az_central + az_j2,
    )


def state_derivative_3d_j2(
    state: State3DJ2,
) -> State3DJ2:
    """Return the derivative of a J2-perturbed spacecraft state."""

    ax, ay, az = total_acceleration_3d_j2(
        state.x,
        state.y,
        state.z,
    )

    return State3DJ2(
        x=state.vx,
        y=state.vy,
        z=state.vz,
        vx=ax,
        vy=ay,
        vz=az,
    )


def rk4_step_3d_j2(
    state: State3DJ2,
    dt: float,
) -> State3DJ2:
    """Advance a J2-perturbed spacecraft state by one RK4 timestep."""

    if dt <= 0:
        raise ValueError(
            "Timestep must be greater than zero."
        )

    k1 = state_derivative_3d_j2(state)

    k2 = state_derivative_3d_j2(
        State3DJ2(
            state.x + 0.5 * dt * k1.x,
            state.y + 0.5 * dt * k1.y,
            state.z + 0.5 * dt * k1.z,
            state.vx + 0.5 * dt * k1.vx,
            state.vy + 0.5 * dt * k1.vy,
            state.vz + 0.5 * dt * k1.vz,
        )
    )

    k3 = state_derivative_3d_j2(
        State3DJ2(
            state.x + 0.5 * dt * k2.x,
            state.y + 0.5 * dt * k2.y,
            state.z + 0.5 * dt * k2.z,
            state.vx + 0.5 * dt * k2.vx,
            state.vy + 0.5 * dt * k2.vy,
            state.vz + 0.5 * dt * k2.vz,
        )
    )

    k4 = state_derivative_3d_j2(
        State3DJ2(
            state.x + dt * k3.x,
            state.y + dt * k3.y,
            state.z + dt * k3.z,
            state.vx + dt * k3.vx,
            state.vy + dt * k3.vy,
            state.vz + dt * k3.vz,
        )
    )

    return State3DJ2(
        x=state.x + dt / 6 * (
            k1.x + 2 * k2.x + 2 * k3.x + k4.x
        ),
        y=state.y + dt / 6 * (
            k1.y + 2 * k2.y + 2 * k3.y + k4.y
        ),
        z=state.z + dt / 6 * (
            k1.z + 2 * k2.z + 2 * k3.z + k4.z
        ),
        vx=state.vx + dt / 6 * (
            k1.vx + 2 * k2.vx + 2 * k3.vx + k4.vx
        ),
        vy=state.vy + dt / 6 * (
            k1.vy + 2 * k2.vy + 2 * k3.vy + k4.vy
        ),
        vz=state.vz + dt / 6 * (
            k1.vz + 2 * k2.vz + 2 * k3.vz + k4.vz
        ),
    )