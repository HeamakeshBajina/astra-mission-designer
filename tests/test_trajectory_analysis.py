import math

from astra.physics.constants import EARTH_RADIUS
from astra.physics.orbital import circular_orbital_velocity
from astra.simulation.propagator import State
from astra.simulation.trajectory import propagate_trajectory
from astra.simulation.trajectory_analysis import analyze_trajectory


def create_test_trajectory():
    velocity = circular_orbital_velocity(EARTH_RADIUS)

    initial = State(
        x=EARTH_RADIUS,
        y=0,
        vx=0,
        vy=velocity,
    )

    return propagate_trajectory(
        initial_state=initial,
        duration=10,
        dt=1,
    )


def test_analysis_has_one_value_per_state():
    trajectory = create_test_trajectory()
    result = analyze_trajectory(trajectory)

    assert len(result.radii) == len(trajectory.states)
    assert len(result.altitudes) == len(trajectory.states)
    assert len(result.speeds) == len(trajectory.states)
    assert len(result.specific_energies) == len(trajectory.states)


def test_initial_radius_is_correct():
    trajectory = create_test_trajectory()
    result = analyze_trajectory(trajectory)

    assert math.isclose(result.radii[0], EARTH_RADIUS)


def test_initial_altitude_is_zero():
    trajectory = create_test_trajectory()
    result = analyze_trajectory(trajectory)

    assert math.isclose(result.altitudes[0], 0.0, abs_tol=1e-9)


def test_initial_speed_is_circular_orbital_velocity():
    trajectory = create_test_trajectory()
    result = analyze_trajectory(trajectory)

    expected = circular_orbital_velocity(EARTH_RADIUS)

    assert math.isclose(result.speeds[0], expected)


def test_orbital_energy_is_negative_for_bound_orbit():
    trajectory = create_test_trajectory()
    result = analyze_trajectory(trajectory)

    assert all(energy < 0 for energy in result.specific_energies)


def test_analysis_preserves_approximately_constant_energy():
    trajectory = create_test_trajectory()
    result = analyze_trajectory(trajectory)

    initial_energy = result.specific_energies[0]
    final_energy = result.specific_energies[-1]

    assert math.isclose(
        final_energy,
        initial_energy,
        rel_tol=1e-10,
    )