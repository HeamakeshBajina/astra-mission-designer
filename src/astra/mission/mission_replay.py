"""Mission replay utilities for ASTRA."""

from dataclasses import dataclass

from astra.physics.orbital_elements import (
    OrbitalElements,
    orbital_elements_from_state,
)
from astra.simulation.trajectory_history import (
    TrajectoryHistory,
    TrajectoryPoint,
)


@dataclass(frozen=True)
class ReplayFrame:
    """A spacecraft state exposed at a mission replay time."""

    time: float
    state: object
    orbital_elements: OrbitalElements


class MissionReplay:
    """Replay and inspect a completed spacecraft trajectory."""

    def __init__(
        self,
        history: TrajectoryHistory,
    ) -> None:
        """Create a replay controller for a trajectory history."""

        if history.point_count <= 0:
            raise ValueError(
                "Trajectory history cannot be empty."
            )

        self._history = history

    @property
    def history(self) -> TrajectoryHistory:
        """Return the underlying trajectory history."""

        return self._history

    @property
    def duration(self) -> float:
        """Return the total mission duration."""

        return self._history.final_time

    @property
    def frame_count(self) -> int:
        """Return the number of recorded replay frames."""

        return self._history.point_count

    @property
    def start_time(self) -> float:
        """Return the replay start time."""

        return self._history.times[0]

    @property
    def end_time(self) -> float:
        """Return the replay end time."""

        return self._history.final_time

    def _validate_time(
        self,
        time: float,
    ) -> None:
        """Validate a requested replay time."""

        if time < self.start_time:
            raise ValueError(
                "Replay time cannot be before the trajectory start."
            )

        if time > self.end_time:
            raise ValueError(
                "Replay time cannot exceed the trajectory end."
            )

    def frame_at(
        self,
        time: float,
    ) -> ReplayFrame:
        """Return the recorded frame nearest to a requested time."""

        self._validate_time(time)

        nearest_point = min(
            self._history.points,
            key=lambda point: abs(point.time - time),
        )

        return ReplayFrame(
            time=nearest_point.time,
            state=nearest_point.state,
            orbital_elements=orbital_elements_from_state(
                nearest_point.state
            ),
        )

    def frame_at_index(
        self,
        index: int,
    ) -> ReplayFrame:
        """Return a replay frame by trajectory index."""

        if index < 0:
            raise ValueError(
                "Replay frame index cannot be negative."
            )

        if index >= self.frame_count:
            raise ValueError(
                "Replay frame index is outside the trajectory."
            )

        point = self._history.points[index]

        return ReplayFrame(
            time=point.time,
            state=point.state,
            orbital_elements=orbital_elements_from_state(
                point.state
            ),
        )

    def frames(
        self,
    ) -> tuple[ReplayFrame, ...]:
        """Return every trajectory point as a replay frame."""

        return tuple(
            ReplayFrame(
                time=point.time,
                state=point.state,
                orbital_elements=orbital_elements_from_state(
                    point.state
                ),
            )
            for point in self._history.points
        )

    def position_at(
        self,
        time: float,
    ) -> tuple[float, float, float]:
        """Return spacecraft position at the nearest recorded time."""

        frame = self.frame_at(time)
        state = frame.state

        return (
            state.x,
            state.y,
            state.z,
        )

    def velocity_at(
        self,
        time: float,
    ) -> tuple[float, float, float]:
        """Return spacecraft velocity at the nearest recorded time."""

        frame = self.frame_at(time)
        state = frame.state

        return (
            state.vx,
            state.vy,
            state.vz,
        )

    def mass_at(
        self,
        time: float,
    ) -> float:
        """Return spacecraft mass at the nearest recorded time."""

        return self.frame_at(time).state.mass

    def orbital_elements_at(
        self,
        time: float,
    ) -> OrbitalElements:
        """Return orbital elements at the nearest recorded time."""

        return self.frame_at(time).orbital_elements


def create_mission_replay(
    history: TrajectoryHistory,
) -> MissionReplay:
    """Create a replay controller from a trajectory history."""

    return MissionReplay(history)
