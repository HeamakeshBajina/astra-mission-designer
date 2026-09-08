"""3D finite-duration thrust propagation for ASTRA."""

from dataclasses import dataclass
import math

from astra.physics.burn_vector import (
    BurnVector,
    resolve_burn_direction,
)
from astra.physics.constants import EARTH_MU
from astra.physics.thrust import ThrustModel
from astra.simulation.finite_burn import FiniteBurn


@dataclass(frozen=True)
class State3DThrust:
    """Spacecraft state in 3D position, velocity, and mass."""

    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    mass: float


def _derivatives(
    state: State3DThrust,
    thrust_model: ThrustModel,
    thrust_direction: BurnVector | tuple[float, float, float],
) -> State3DThrust:
    """Return state derivatives for gravity plus constant thrust."""

    x = state.x
    y = state.y
    z = state.z

    radius = math.sqrt(
        x * x +
        y * y +
        z * z
    )

    if radius <= 0:
        raise ValueError(
            "Spacecraft position cannot be at the Earth's center."
        )

    if state.mass <= 0:
        raise ValueError(
            "Spacecraft mass must be greater than zero."
        )

    ux, uy, uz = resolve_burn_direction(
        thrust_direction
    )

    gravity_factor = -EARTH_MU / radius**3

    ax_gravity = gravity_factor * x
    ay_gravity = gravity_factor * y
    az_gravity = gravity_factor * z

    acceleration_from_thrust = (
        thrust_model.thrust / state.mass
    )

    ax_thrust = acceleration_from_thrust * ux
    ay_thrust = acceleration_from_thrust * uy
    az_thrust = acceleration_from_thrust * uz

    return State3DThrust(
        x=state.vx,
        y=state.vy,
        z=state.vz,
        vx=ax_gravity + ax_thrust,
        vy=ay_gravity + ay_thrust,
        vz=az_gravity + az_thrust,
        mass=-thrust_model.mass_flow_rate,
    )


def _add_scaled(
    state: State3DThrust,
    derivative: State3DThrust,
    scale: float,
) -> State3DThrust:
    """Return state + derivative * scale."""

    return State3DThrust(
        x=state.x + derivative.x * scale,
        y=state.y + derivative.y * scale,
        z=state.z + derivative.z * scale,
        vx=state.vx + derivative.vx * scale,
        vy=state.vy + derivative.vy * scale,
        vz=state.vz + derivative.vz * scale,
        mass=state.mass + derivative.mass * scale,
    )


def rk4_step_thrust(
    state: State3DThrust,
    dt: float,
    thrust_model: ThrustModel,
    thrust_direction: BurnVector | tuple[float, float, float],
    dry_mass: float | None = None,
) -> State3DThrust:
    """Advance a finite-thrust 3D state by one RK4 timestep."""

    if dt <= 0:
        raise ValueError(
            "Timestep must be greater than zero."
        )

    if dry_mass is not None:
        if dry_mass <= 0:
            raise ValueError(
                "Dry mass must be greater than zero."
            )

        burn = FiniteBurn(
            thrust_model=thrust_model,
            duration=dt,
            dry_mass=dry_mass,
        )

        if not burn.can_complete(state.mass):
            raise ValueError(
                "Timestep requires more propellant than available."
            )

    # Validate the direction once before integration.
    resolve_burn_direction(thrust_direction)

    k1 = _derivatives(
        state,
        thrust_model,
        thrust_direction,
    )

    k2_state = _add_scaled(
        state,
        k1,
        dt / 2.0,
    )

    k2 = _derivatives(
        k2_state,
        thrust_model,
        thrust_direction,
    )

    k3_state = _add_scaled(
        state,
        k2,
        dt / 2.0,
    )

    k3 = _derivatives(
        k3_state,
        thrust_model,
        thrust_direction,
    )

    k4_state = _add_scaled(
        state,
        k3,
        dt,
    )

    k4 = _derivatives(
        k4_state,
        thrust_model,
        thrust_direction,
    )

    return State3DThrust(
        x=state.x + (
            dt / 6.0
        ) * (
            k1.x +
            2.0 * k2.x +
            2.0 * k3.x +
            k4.x
        ),
        y=state.y + (
            dt / 6.0
        ) * (
            k1.y +
            2.0 * k2.y +
            2.0 * k3.y +
            k4.y
        ),
        z=state.z + (
            dt / 6.0
        ) * (
            k1.z +
            2.0 * k2.z +
            2.0 * k3.z +
            k4.z
        ),
        vx=state.vx + (
            dt / 6.0
        ) * (
            k1.vx +
            2.0 * k2.vx +
            2.0 * k3.vx +
            k4.vx
        ),
        vy=state.vy + (
            dt / 6.0
        ) * (
            k1.vy +
            2.0 * k2.vy +
            2.0 * k3.vy +
            k4.vy
        ),
        vz=state.vz + (
            dt / 6.0
        ) * (
            k1.vz +
            2.0 * k2.vz +
            2.0 * k3.vz +
            k4.vz
        ),
        mass=state.mass + (
            dt / 6.0
        ) * (
            k1.mass +
            2.0 * k2.mass +
            2.0 * k3.mass +
            k4.mass
        ),
    )
