"""Physics validation tests for ASTRA's 3D orbital propagator."""

import math

import pytest

from astra.physics.constants import EARTH_MU
from astra.simulation.propagator_3d import State3D, rk4_step_3d


def orbital_radius(state: State3D) -> float:
    """Return spacecraft distance from Earth's center."""

    return math.sqrt(
        state.x**2
        + state.y**2
        + state.z**2
    )


def orbital_speed(state: State3D) -> float:
    """Return spacecraft speed."""

    return math.sqrt(
        state.vx**2
        + state.vy**2
        + state.vz**2
    )


def specific_orbital_energy(state: State3D) -> float:
    """Return specific orbital energy."""

    radius = orbital_radius(state)
    speed = orbital_speed(state)

    return (
        speed**2 / 2
        - EARTH_MU / radius
    )


def specific_angular_momentum(state: State3D) -> tuple[float, float, float]:
    """Return the specific angular momentum vector."""

    hx = state.y * state.vz - state.z * state.vy
    hy = state.z * state.vx - state.x * state.vz
    hz = state.x * state.vy - state.y * state.vx

    return hx, hy, hz


def vector_magnitude(vector: tuple[float, float, float]) -> float:
    """Return the magnitude of a 3D vector."""

    return math.sqrt(
        sum(component**2 for component in vector)
    )


def propagate(
    state: State3D,
    duration: float,
    dt: float,
) -> State3D:
    """Propagate a state for a specified duration."""

    steps = int(duration / dt)

    for _ in range(steps):
        state = rk4_step_3d(state, dt)

    return state


def test_circular_orbit_radius_is_stable():
    """A circular orbit should maintain approximately constant radius."""

    radius = 7_000_000.0
    speed = math.sqrt(EARTH_MU / radius)

    state = State3D(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=speed,
        vz=0.0,
    )

    initial_radius = orbital_radius(state)

    state = propagate(
        state,
        duration=600.0,
        dt=1.0,
    )

    final_radius = orbital_radius(state)

    assert final_radius == pytest.approx(
        initial_radius,
        rel=1e-7,
    )


def test_specific_energy_is_conserved():
    """Two-body orbital energy should remain nearly constant."""

    radius = 7_000_000.0
    speed = math.sqrt(EARTH_MU / radius)

    state = State3D(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=speed,
        vz=0.0,
    )

    initial_energy = specific_orbital_energy(state)

    state = propagate(
        state,
        duration=3600.0,
        dt=10.0,
    )

    final_energy = specific_orbital_energy(state)

    assert final_energy == pytest.approx(
        initial_energy,
        rel=1e-9,
    )


def test_specific_angular_momentum_is_conserved():
    """Two-body orbital angular momentum should remain nearly constant."""

    radius = 7_000_000.0
    speed = math.sqrt(EARTH_MU / radius)

    state = State3D(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=speed,
        vz=0.0,
    )

    initial_h = specific_angular_momentum(state)
    initial_h_magnitude = vector_magnitude(initial_h)

    state = propagate(
        state,
        duration=3600.0,
        dt=10.0,
    )

    final_h = specific_angular_momentum(state)
    final_h_magnitude = vector_magnitude(final_h)

    assert final_h_magnitude == pytest.approx(
        initial_h_magnitude,
        rel=1e-9,
    )


def test_inclined_orbit_preserves_three_dimensional_motion():
    """An inclined orbit should retain meaningful z motion."""

    radius = 7_000_000.0
    speed = math.sqrt(EARTH_MU / radius)
    inclination = math.radians(45.0)

    state = State3D(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=speed * math.cos(inclination),
        vz=speed * math.sin(inclination),
    )

    state = propagate(
        state,
        duration=1800.0,
        dt=10.0,
    )

    assert abs(state.z) > 1_000.0
    assert abs(state.vz) > 0.1


def test_smaller_timestep_improves_numerical_accuracy():
    """A smaller timestep should produce a more accurate result."""

    radius = 7_000_000.0
    speed = math.sqrt(EARTH_MU / radius)

    initial_state = State3D(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=speed,
        vz=0.0,
    )

    coarse = propagate(
        initial_state,
        duration=600.0,
        dt=20.0,
    )

    fine = propagate(
        initial_state,
        duration=600.0,
        dt=5.0,
    )

    coarse_error = abs(
        orbital_radius(coarse) - radius
    )

    fine_error = abs(
        orbital_radius(fine) - radius
    )

    assert fine_error <= coarse_error