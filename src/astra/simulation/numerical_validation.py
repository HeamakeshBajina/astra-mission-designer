"""Numerical validation and timestep convergence tools for ASTRA."""

from dataclasses import dataclass
import math
from collections.abc import Callable

from astra.simulation.propagator_3d_thrust import (
    State3DThrust,
    rk4_step_thrust,
)
from astra.simulation.propagator_3d_thrust_j2 import (
    State3DThrustJ2,
    rk4_step_thrust_j2,
)
from astra.physics.thrust import ThrustModel


@dataclass(frozen=True)
class ConvergenceResult:
    """Result of a timestep convergence study."""

    coarse_dt: float
    medium_dt: float
    fine_dt: float
    coarse_error: float
    medium_error: float
    convergence_ratio: float
    converged: bool


@dataclass(frozen=True)
class StateError:
    """Numerical difference between two propagated states."""

    position_error: float
    velocity_error: float
    mass_error: float


def _vector_error(
    first: tuple[float, ...],
    second: tuple[float, ...],
) -> float:
    """Return Euclidean error between two vectors."""
    if len(first) != len(second):
        raise ValueError("State vectors must have the same dimension.")

    return math.sqrt(
        sum(
            (a - b) ** 2
            for a, b in zip(first, second)
        )
    )


def state_error(
    first: State3DThrust,
    second: State3DThrust,
) -> StateError:
    """Return position, velocity, and mass differences."""
    position_error = _vector_error(
        (first.x, first.y, first.z),
        (second.x, second.y, second.z),
    )
    velocity_error = _vector_error(
        (first.vx, first.vy, first.vz),
        (second.vx, second.vy, second.vz),
    )
    mass_error = abs(first.mass - second.mass)

    return StateError(
        position_error=position_error,
        velocity_error=velocity_error,
        mass_error=mass_error,
    )


def state_error_j2(
    first: State3DThrustJ2,
    second: State3DThrustJ2,
) -> StateError:
    """Return position, velocity, and mass differences for J2 states."""
    position_error = _vector_error(
        (first.x, first.y, first.z),
        (second.x, second.y, second.z),
    )
    velocity_error = _vector_error(
        (first.vx, first.vy, first.vz),
        (second.vx, second.vy, second.vz),
    )
    mass_error = abs(first.mass - second.mass)

    return StateError(
        position_error=position_error,
        velocity_error=velocity_error,
        mass_error=mass_error,
    )


def propagate_to_time(
    initial_state: State3DThrust,
    duration: float,
    dt: float,
    thrust_model: ThrustModel,
    thrust_direction: tuple[float, float, float],
    dry_mass: float | None = None,
) -> State3DThrust:
    """Propagate a finite-thrust state to an exact final time."""
    if duration < 0:
        raise ValueError("Duration cannot be negative.")
    if dt <= 0:
        raise ValueError("Timestep must be greater than zero.")

    current_state = initial_state
    elapsed = 0.0

    while elapsed < duration:
        step = min(dt, duration - elapsed)

        current_state = rk4_step_thrust(
            state=current_state,
            dt=step,
            thrust_model=thrust_model,
            thrust_direction=thrust_direction,
            dry_mass=dry_mass,
        )

        elapsed += step

    return current_state


def propagate_to_time_j2(
    initial_state: State3DThrustJ2,
    duration: float,
    dt: float,
    thrust_model: ThrustModel,
    thrust_direction: tuple[float, float, float],
    dry_mass: float | None = None,
) -> State3DThrustJ2:
    """Propagate a J2 finite-thrust state to an exact final time."""
    if duration < 0:
        raise ValueError("Duration cannot be negative.")
    if dt <= 0:
        raise ValueError("Timestep must be greater than zero.")

    current_state = initial_state
    elapsed = 0.0

    while elapsed < duration:
        step = min(dt, duration - elapsed)

        current_state = rk4_step_thrust_j2(
            state=current_state,
            dt=step,
            thrust_model=thrust_model,
            thrust_direction=thrust_direction,
            dry_mass=dry_mass,
        )

        elapsed += step

    return current_state


def timestep_convergence(
    propagate: Callable[[float], object],
    coarse_dt: float,
    medium_dt: float,
    fine_dt: float,
    error_function: Callable[[object, object], float],
    tolerance: float = 1e-6,
) -> ConvergenceResult:
    """Evaluate numerical convergence across three timestep sizes."""
    if coarse_dt <= 0 or medium_dt <= 0 or fine_dt <= 0:
        raise ValueError("Timesteps must be greater than zero.")

    if not (
        coarse_dt > medium_dt > fine_dt
    ):
        raise ValueError(
            "Timesteps must satisfy coarse > medium > fine."
        )

    if tolerance <= 0:
        raise ValueError("Tolerance must be greater than zero.")

    coarse_state = propagate(coarse_dt)
    medium_state = propagate(medium_dt)
    fine_state = propagate(fine_dt)

    coarse_error = error_function(
        coarse_state,
        fine_state,
    )
    medium_error = error_function(
        medium_state,
        fine_state,
    )

    if medium_error == 0:
        convergence_ratio = math.inf
    else:
        convergence_ratio = (
            coarse_error / medium_error
        )

    converged = (
        medium_error <= tolerance
        and convergence_ratio > 1.0
    )

    return ConvergenceResult(
        coarse_dt=coarse_dt,
        medium_dt=medium_dt,
        fine_dt=fine_dt,
        coarse_error=coarse_error,
        medium_error=medium_error,
        convergence_ratio=convergence_ratio,
        converged=converged,
    )
