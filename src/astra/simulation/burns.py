"""Velocity-change models for ASTRA."""

import math

from astra.simulation.propagator import State


def apply_prograde_burn(
    state: State,
    delta_v: float,
) -> State:
    """Apply an instantaneous prograde velocity change."""

    if delta_v < 0:
        raise ValueError("Delta-v cannot be negative.")

    speed = math.hypot(state.vx, state.vy)

    if speed <= 0:
        raise ValueError(
            "A prograde burn requires a non-zero velocity."
        )

    unit_vx = state.vx / speed
    unit_vy = state.vy / speed

    return State(
        x=state.x,
        y=state.y,
        vx=state.vx + delta_v * unit_vx,
        vy=state.vy + delta_v * unit_vy,
    )


def apply_retrograde_burn(
    state: State,
    delta_v: float,
) -> State:
    """Apply an instantaneous retrograde velocity change."""

    if delta_v < 0:
        raise ValueError("Delta-v cannot be negative.")

    speed = math.hypot(state.vx, state.vy)

    if speed <= 0:
        raise ValueError(
            "A retrograde burn requires a non-zero velocity."
        )

    unit_vx = state.vx / speed
    unit_vy = state.vy / speed

    return State(
        x=state.x,
        y=state.y,
        vx=state.vx - delta_v * unit_vx,
        vy=state.vy - delta_v * unit_vy,
    )