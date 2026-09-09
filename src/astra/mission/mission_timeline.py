"""Mission timeline primitives for ASTRA."""

from dataclasses import dataclass
from enum import Enum


class MissionEventType(str, Enum):
    """Supported mission event types."""

    BURN = "burn"
    COAST = "coast"


@dataclass(frozen=True)
class MissionEvent:
    """A time-ordered event in a spacecraft mission."""

    name: str
    start_time: float
    duration: float
    event_type: MissionEventType

    def __post_init__(self) -> None:
        """Validate mission event parameters."""

        if not self.name.strip():
            raise ValueError(
                "Event name cannot be empty."
            )

        if self.start_time < 0:
            raise ValueError(
                "Event start time cannot be negative."
            )

        if self.duration < 0:
            raise ValueError(
                "Event duration cannot be negative."
            )

    @property
    def end_time(self) -> float:
        """Return the absolute end time of the event."""

        return self.start_time + self.duration


@dataclass(frozen=True)
class MissionTimeline:
    """Validated ordered sequence of mission events."""

    events: list[MissionEvent]

    @property
    def duration(self) -> float:
        """Return the total mission duration."""

        if not self.events:
            return 0.0

        return max(
            event.end_time
            for event in self.events
        )

    @property
    def event_count(self) -> int:
        """Return the number of mission events."""

        return len(self.events)

    @property
    def burn_count(self) -> int:
        """Return the number of burn events."""

        return sum(
            event.event_type == MissionEventType.BURN
            for event in self.events
        )

    @property
    def coast_count(self) -> int:
        """Return the number of coast events."""

        return sum(
            event.event_type == MissionEventType.COAST
            for event in self.events
        )


def create_mission_timeline(
    events: list[MissionEvent],
) -> MissionTimeline:
    """Create and validate an ordered mission timeline."""

    if not events:
        raise ValueError(
            "Mission timeline cannot be empty."
        )

    previous_end_time = 0.0

    for event in events:
        if event.start_time < previous_end_time:
            raise ValueError(
                "Mission events cannot overlap."
            )

        previous_end_time = event.end_time

    return MissionTimeline(
        events=list(events),
    )
