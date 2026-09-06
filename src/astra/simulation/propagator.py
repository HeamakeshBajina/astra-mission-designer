"""Numerical orbital propagation for ASTRA."""

from dataclasses import dataclass

import numpy as np

from astra.physics.constants import EARTH_MU


@dataclass(frozen=True)
class State:
    """Spacecraft state in two-dimensional Cartesian coordinates."""

    x: float
    y: float
    vx: float
    vy: float


def gravitational_acceleration(
    x: float,
    y: float,
) -> tuple[float, float]:
    """Calculate Earth's gravitational acceleration."""

    radius_squared = x**2 + y**2

    if radius_squared <= 0:
        raise ValueError("Position cannot be at Earth's center.")

    radius = np.sqrt(radius_squared)
    factor = -EARTH_MU / radius**3

    return factor * x, factor * y


def state_derivative(state: State) -> State:
    """Return the time derivative of a spacecraft state."""

    ax, ay = gravitational_acceleration(
        state.x,
        state.y,
    )

    return State(
        x=state.vx,
        y=state.vy,
        vx=ax,
        vy=ay,
    )


def rk4_step(
    state: State,
    dt: float,
) -> State:
    """Advance a spacecraft state by one RK4 timestep."""

    k1 = state_derivative(state)

    k2 = state_derivative(
        State(
            state.x + 0.5 * dt * k1.x,
            state.y + 0.5 * dt * k1.y,
            state.vx + 0.5 * dt * k1.vx,
            state.vy + 0.5 * dt * k1.vy,
        )
    )

    k3 = state_derivative(
        State(
            state.x + 0.5 * dt * k2.x,
            state.y + 0.5 * dt * k2.y,
            state.vx + 0.5 * dt * k2.vx,
            state.vy + 0.5 * dt * k2.vy,
        )
    )

    k4 = state_derivative(
        State(
            state.x + dt * k3.x,
            state.y + dt * k3.y,
            state.vx + dt * k3.vx,
            state.vy + dt * k3.vy,
        )
    )

    return State(
        x=state.x + dt / 6 * (
            k1.x + 2 * k2.x + 2 * k3.x + k4.x
        ),
        y=state.y + dt / 6 * (
            k1.y + 2 * k2.y + 2 * k3.y + k4.y
        ),
        vx=state.vx + dt / 6 * (
            k1.vx + 2 * k2.vx + 2 * k3.vx + k4.vx
        ),
        vy=state.vy + dt / 6 * (
            k1.vy + 2 * k2.vy + 2 * k3.vy + k4.vy
        ),
    )