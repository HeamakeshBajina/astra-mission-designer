"""Tests for ASTRA mission timeline primitives."""

import pytest

from astra.mission.mission_timeline import (
    MissionEvent,
    MissionEventType,
    create_mission_timeline,
)


def test_event_end_time() -> None:
    event = MissionEvent(
        name="Burn 1",
        start_time=100.0,
        duration=20.0,
        event_type=MissionEventType.BURN,
    )

    assert event.end_time == 120.0


def test_event_rejects_negative_start_time() -> None:
    with pytest.raises(ValueError, match="start time"):
        MissionEvent(
            name="Burn",
            start_time=-1.0,
            duration=10.0,
            event_type=MissionEventType.BURN,
        )


def test_event_rejects_negative_duration() -> None:
    with pytest.raises(ValueError, match="duration"):
        MissionEvent(
            name="Coast",
            start_time=0.0,
            duration=-1.0,
            event_type=MissionEventType.COAST,
        )


def test_event_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="name"):
        MissionEvent(
            name="   ",
            start_time=0.0,
            duration=10.0,
            event_type=MissionEventType.COAST,
        )


def test_timeline_preserves_event_order() -> None:
    events = [
        MissionEvent(
            name="Burn 1",
            start_time=0.0,
            duration=10.0,
            event_type=MissionEventType.BURN,
        ),
        MissionEvent(
            name="Coast 1",
            start_time=10.0,
            duration=50.0,
            event_type=MissionEventType.COAST,
        ),
    ]

    timeline = create_mission_timeline(events)

    assert timeline.events == events


def test_timeline_rejects_empty_events() -> None:
    with pytest.raises(ValueError, match="empty"):
        create_mission_timeline([])


def test_timeline_rejects_overlapping_events() -> None:
    events = [
        MissionEvent(
            name="Burn 1",
            start_time=0.0,
            duration=20.0,
            event_type=MissionEventType.BURN,
        ),
        MissionEvent(
            name="Coast 1",
            start_time=10.0,
            duration=30.0,
            event_type=MissionEventType.COAST,
        ),
    ]

    with pytest.raises(ValueError, match="overlap"):
        create_mission_timeline(events)


def test_timeline_allows_back_to_back_events() -> None:
    events = [
        MissionEvent(
            name="Burn 1",
            start_time=0.0,
            duration=20.0,
            event_type=MissionEventType.BURN,
        ),
        MissionEvent(
            name="Coast 1",
            start_time=20.0,
            duration=100.0,
            event_type=MissionEventType.COAST,
        ),
    ]

    timeline = create_mission_timeline(events)

    assert timeline.duration == 120.0


def test_timeline_counts_events() -> None:
    events = [
        MissionEvent(
            name="Burn 1",
            start_time=0.0,
            duration=10.0,
            event_type=MissionEventType.BURN,
        ),
        MissionEvent(
            name="Coast 1",
            start_time=10.0,
            duration=50.0,
            event_type=MissionEventType.COAST,
        ),
        MissionEvent(
            name="Burn 2",
            start_time=60.0,
            duration=15.0,
            event_type=MissionEventType.BURN,
        ),
    ]

    timeline = create_mission_timeline(events)

    assert timeline.event_count == 3
    assert timeline.burn_count == 2
    assert timeline.coast_count == 1
    assert timeline.duration == 75.0


def test_timeline_does_not_mutate_input_list() -> None:
    events = [
        MissionEvent(
            name="Burn",
            start_time=0.0,
            duration=10.0,
            event_type=MissionEventType.BURN,
        )
    ]

    timeline = create_mission_timeline(events)

    assert timeline.events == events
    assert timeline.events is not events
