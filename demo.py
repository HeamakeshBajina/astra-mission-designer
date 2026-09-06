import matplotlib.pyplot as plt

from astra.physics.constants import EARTH_RADIUS
from astra.physics.orbital import circular_orbital_velocity, orbital_period
from astra.simulation.propagator import State
from astra.simulation.trajectory import propagate_trajectory
from astra.visualization import plot_trajectory, plot_trajectory_analysis


radius = EARTH_RADIUS + 400_000
velocity = circular_orbital_velocity(radius)
period = orbital_period(radius)

initial_state = State(
    x=radius,
    y=0,
    vx=0,
    vy=velocity,
)

trajectory = propagate_trajectory(
    initial_state=initial_state,
    duration=period,
    dt=10,
)

plot_trajectory(trajectory)
plot_trajectory_analysis(trajectory)

plt.show()