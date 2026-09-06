import matplotlib

matplotlib.use("Agg")

from astra.physics.constants import EARTH_RADIUS
from astra.physics.orbital import circular_orbital_velocity
from astra.simulation.propagator import State
from astra.simulation.trajectory import propagate_trajectory
from astra.visualization import plot_trajectory


def create_test_trajectory():
    radius = EARTH_RADIUS + 400_000
    velocity = circular_orbital_velocity(radius)

    initial = State(
        x=radius,
        y=0,
        vx=0,
        vy=velocity,
    )

    return propagate_trajectory(
        initial_state=initial,
        duration=100,
        dt=10,
    )


def test_plot_trajectory_returns_figure_and_axis():
    trajectory = create_test_trajectory()

    figure, axis = plot_trajectory(trajectory)

    assert figure is not None
    assert axis is not None


def test_plot_trajectory_contains_spacecraft_path():
    trajectory = create_test_trajectory()

    figure, axis = plot_trajectory(trajectory)

    assert len(axis.lines) == 1
    assert len(axis.lines[0].get_xdata()) == len(trajectory.states)
    assert len(axis.lines[0].get_ydata()) == len(trajectory.states)

    figure.clf()