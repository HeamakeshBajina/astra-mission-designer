"""Three-dimensional numerical orbital propagation for ASTRA."""

from dataclasses import dataclass
import math

from astra.physics.constants import EARTH_MU


@dataclass(frozen=True)
class State3D:
    """Spacecraft state in three-dimensional Cartesian coordinates."""

    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float


def gravitational_acceleration_3d(
    x: float,
    y: float,
    z: float,
) -> tuple[float, float, float]:
    """Calculate Earth's gravitational acceleration in 3D."""

    radius_squared = x**2 + y**2 + z**2

    if radius_squared <= 0:
        raise ValueError("Position cannot be at Earth's center.")

    radius = math.sqrt(radius_squared)
    factor = -EARTH_MU / radius**3

    return (
        factor * x,
        factor * y,
        factor * z,
    )


def state_derivative_3d(state: State3D) -> State3D:
    """Return the time derivative of a 3D spacecraft state."""

    ax, ay, az = gravitational_acceleration_3d(
        state.x,
        state.y,
        state.z,
    )

    return State3D(
        x=state.vx,
        y=state.vy,
        z=state.vz,
        vx=ax,
        vy=ay,
        vz=az,
    )


def rk4_step_3d(
    state: State3D,
    dt: float,
) -> State3D:
    """Advance a 3D spacecraft state by one RK4 timestep."""

    if dt <= 0:
        raise ValueError("Timestep must be greater than zero.")

    k1 = state_derivative_3d(state)

    k2 = state_derivative_3d(
        State3D(
            state.x + 0.5 * dt * k1.x,
            state.y + 0.5 * dt * k1.y,
            state.z + 0.5 * dt * k1.z,
            state.vx + 0.5 * dt * k1.vx,
            state.vy + 0.5 * dt * k1.vy,
            state.vz + 0.5 * dt * k1.vz,
        )
    )

    k3 = state_derivative_3d(
        State3D(
            state.x + 0.5 * dt * k2.x,
            state.y + 0.5 * dt * k2.y,
            state.z + 0.5 * dt * k2.z,
            state.vx + 0.5 * dt * k2.vx,
            state.vy + 0.5 * dt * k2.vy,
            state.vz + 0.5 * dt * k2.vz,
        )
    )

    k4 = state_derivative_3d(
        State3D(
            state.x + dt * k3.x,
            state.y + dt * k3.y,
            state.z + dt * k3.z,
            state.vx + dt * k3.vx,
            state.vy + dt * k3.vy,
            state.vz + dt * k3.vz,
        )
    )

    return State3D(
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