import math

from astra.physics.constants import EARTH_RADIUS
from astra.physics.orbital import (
    circular_orbital_velocity,
    orbital_period,
)
from astra.simulation.propagator import State
from astra.simulation.trajectory import propagate_trajectory
from astra.simulation.trajectory_analysis import analyze_trajectory


def create_circular_orbit_trajectory():
    radius = EARTH_RADIUS + 400_000
    velocity = circular_orbital_velocity(radius)

    initial = State(
        x=radius,
        y=0,
        vx=0,
        vy=velocity,
    )

    period = orbital_period(radius)

    return propagate_trajectory(
        initial_state=initial,
        duration=period,
        dt=10,
    )


def test_circular_orbit_returns_close_to_start():
    trajectory = create_circular_orbit_trajectory()

    initial = trajectory.states[0]
    final = trajectory.states[-1]

    initial_radius = math.hypot(initial.x, initial.y)
    final_radius = math.hypot(final.x, final.y)

    assert math.isclose(
        final_radius,
        initial_radius,
        rel_tol=1e-6,
    )


def test_circular_orbit_speed_remains_stable():
    trajectory = create_circular_orbit_trajectory()

    analysis = analyze_trajectory(trajectory)

    initial_speed = analysis.speeds[0]
    final_speed = analysis.speeds[-1]

    assert math.isclose(
        final_speed,
        initial_speed,
        rel_tol=1e-6,
    )


def test_circular_orbit_energy_remains_stable():
    trajectory = create_circular_orbit_trajectory()

    analysis = analyze_trajectory(trajectory)

    initial_energy = analysis.specific_energies[0]
    final_energy = analysis.specific_energies[-1]

    assert math.isclose(
        final_energy,
        initial_energy,
        rel_tol=1e-8,
    )