"""Tests for ASTRA mission replay."""

import math

import pytest

from astra.physics.burn_vector import BurnVector
from astra.physics.constants import EARTH_MU, EARTH_RADIUS
from astra.physics.orbital_elements import OrbitalElements
from astra.physics.thrust import ThrustModel
from astra.mission.mission_replay import (
    MissionReplay,
    ReplayFrame,
    create_mission_replay,
)
from astra.simulation.propagator_3d_thrust import State3DThrust
from astra.simulation.trajectory_history import (
    simulate_trajectory,
)


def circular_state(
    altitude: float = 400_000.0,
) -> State3DThrust:
    """Return a circular equatorial orbit state."""

    radius = EARTH_RADIUS + altitude
    velocity = math.sqrt(
        EARTH_MU / radius
    )

    return State3DThrust(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=velocity,
        vz=0.0,
        mass=500.0,
    )


def make_history():
    """Create a deterministic trajectory for replay tests."""

    return simulate_trajectory(
        initial_state=circular_state(),
        duration=10.0,
        timestep=1.0,
        thrust_model=ThrustModel(
            thrust=0.0,
            specific_impulse=300.0,
        ),
        thrust_direction=BurnVector(
            1.0,
            0.0,
            0.0,
        ),
    )


def test_replay_stores_history() -> None:
    """Replay should retain the supplied trajectory history."""

    history = make_history()
    replay = MissionReplay(history)

    assert replay.history is history


def test_replay_reports_duration() -> None:
    """Replay duration should match the recorded trajectory."""

    replay = MissionReplay(make_history())

    assert replay.duration == pytest.approx(10.0)
    assert replay.start_time == pytest.approx(0.0)
    assert replay.end_time == pytest.approx(10.0)


def test_replay_reports_frame_count() -> None:
    """Replay should expose the trajectory point count."""

    replay = MissionReplay(make_history())

    assert replay.frame_count == 11


def test_frame_at_exact_time() -> None:
    """Exact recorded times should return the corresponding frame."""

    replay = MissionReplay(make_history())

    frame = replay.frame_at(5.0)

    assert isinstance(frame, ReplayFrame)
    assert frame.time == pytest.approx(5.0)


def test_frame_at_uses_nearest_recorded_time() -> None:
    """Non-recorded times should select the nearest trajectory point."""

    replay = MissionReplay(make_history())

    frame = replay.frame_at(5.4)

    assert frame.time == pytest.approx(5.0)


def test_frame_at_handles_upper_half_tie() -> None:
    """A time closer to the next frame should select that frame."""

    replay = MissionReplay(make_history())

    frame = replay.frame_at(5.6)

    assert frame.time == pytest.approx(6.0)


def test_frame_at_rejects_time_before_start() -> None:
    """Times before the mission must be rejected."""

    replay = MissionReplay(make_history())

    with pytest.raises(
        ValueError,
        match="before",
    ):
        replay.frame_at(-1.0)


def test_frame_at_rejects_time_after_end() -> None:
    """Times after the mission must be rejected."""

    replay = MissionReplay(make_history())

    with pytest.raises(
        ValueError,
        match="exceed",
    ):
        replay.frame_at(11.0)


def test_frame_at_index_returns_correct_frame() -> None:
    """Index lookup should return the requested trajectory point."""

    replay = MissionReplay(make_history())

    frame = replay.frame_at_index(3)

    assert frame.time == pytest.approx(3.0)


def test_frame_at_index_rejects_negative_index() -> None:
    """Negative replay indices must be rejected."""

    replay = MissionReplay(make_history())

    with pytest.raises(
        ValueError,
        match="negative",
    ):
        replay.frame_at_index(-1)


def test_frame_at_index_rejects_out_of_range_index() -> None:
    """Indices beyond the trajectory must be rejected."""

    replay = MissionReplay(make_history())

    with pytest.raises(
        ValueError,
        match="outside",
    ):
        replay.frame_at_index(11)


def test_frames_returns_every_recorded_frame() -> None:
    """Replay should expose every recorded state."""

    replay = MissionReplay(make_history())

    frames = replay.frames()

    assert len(frames) == replay.frame_count
    assert frames[0].time == pytest.approx(0.0)
    assert frames[-1].time == pytest.approx(10.0)


def test_position_at_returns_position() -> None:
    """Position lookup should expose the selected state position."""

    replay = MissionReplay(make_history())

    position = replay.position_at(4.0)

    assert position == replay.history.positions[4]


def test_velocity_at_returns_velocity() -> None:
    """Velocity lookup should expose the selected state velocity."""

    replay = MissionReplay(make_history())

    velocity = replay.velocity_at(4.0)

    assert velocity == replay.history.velocities[4]


def test_mass_at_returns_mass() -> None:
    """Mass lookup should expose the selected spacecraft mass."""

    replay = MissionReplay(make_history())

    assert replay.mass_at(4.0) == pytest.approx(500.0)


def test_orbital_elements_are_available() -> None:
    """Replay should calculate orbital elements for each frame."""

    replay = MissionReplay(make_history())

    elements = replay.orbital_elements_at(5.0)

    assert isinstance(
        elements,
        OrbitalElements,
    )
    assert elements.semi_major_axis > 0
    assert elements.eccentricity >= 0
    assert 0 <= elements.inclination <= 180


def test_each_frame_contains_orbital_elements() -> None:
    """Every replay frame should contain orbital elements."""

    replay = MissionReplay(make_history())

    frames = replay.frames()

    assert all(
        isinstance(
            frame.orbital_elements,
            OrbitalElements,
        )
        for frame in frames
    )


def test_create_mission_replay_returns_replay() -> None:
    """Factory should return a MissionReplay instance."""

    replay = create_mission_replay(
        make_history()
    )

    assert isinstance(
        replay,
        MissionReplay,
    )


def test_replay_supports_initial_state() -> None:
    """Replay should reproduce the initial spacecraft position."""

    history = make_history()
    replay = MissionReplay(history)

    assert replay.position_at(0.0) == history.positions[0]


def test_replay_supports_final_state() -> None:
    """Replay should reproduce the final spacecraft position."""

    history = make_history()
    replay = MissionReplay(history)

    assert replay.position_at(
        history.final_time
    ) == history.positions[-1]


def test_replay_frames_are_immutable() -> None:
    """Replay frames should be frozen dataclass instances."""

    replay = MissionReplay(make_history())
    frame = replay.frame_at(2.0)

    with pytest.raises(
        AttributeError,
    ):
        frame.time = 99.0


def test_replay_rejects_empty_history_like_input() -> None:
    """Invalid replay input should be rejected."""

    with pytest.raises(
        AttributeError,
    ):
        MissionReplay(None)  # type: ignore[arg-type]
