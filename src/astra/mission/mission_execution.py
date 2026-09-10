"""Mission-level spacecraft execution engine for ASTRA."""

from dataclasses import dataclass

from astra.physics.burn_vector import BurnVector
from astra.physics.thrust import ThrustModel
from astra.mission.mission_timeline import (
    MissionEvent,
    MissionEventType,
    MissionTimeline,
)
from astra.simulation.trajectory_history import (
    TrajectoryHistory,
    TrajectoryPoint,
    simulate_trajectory,
    simulate_trajectory_j2,
)
from astra.simulation.propagator_3d_thrust import State3DThrust


@dataclass(frozen=True)
class MissionExecutionEvent:
    """Executable configuration for one mission timeline event."""

    event: MissionEvent
    thrust_model: ThrustModel | None = None
    burn_direction: BurnVector | None = None
    dry_mass: float | None = None

    def __post_init__(self) -> None:
        """Validate event-specific execution parameters."""

        if self.event.event_type == MissionEventType.BURN:
            if self.thrust_model is None:
                raise ValueError(
                    "Burn events require a thrust model."
                )

            if self.burn_direction is None:
                raise ValueError(
                    "Burn events require a burn direction."
                )

            if self.burn_direction.magnitude <= 0:
                raise ValueError(
                    "Burn direction cannot be the zero vector."
                )

            if self.dry_mass is None:
                raise ValueError(
                    "Burn events require a dry mass."
                )

            if self.dry_mass <= 0:
                raise ValueError(
                    "Dry mass must be greater than zero."
                )


@dataclass(frozen=True)
class MissionExecutionPlan:
    """Validated executable spacecraft mission plan."""

    events: tuple[MissionExecutionEvent, ...]

    def __post_init__(self) -> None:
        """Validate event ordering and timeline consistency."""

        if not self.events:
            raise ValueError(
                "Mission execution plan cannot be empty."
            )

        previous_end_time = 0.0

        for execution_event in self.events:
            event = execution_event.event

            if event.start_time < previous_end_time:
                raise ValueError(
                    "Mission execution events cannot overlap."
                )

            previous_end_time = event.end_time

    @property
    def duration(self) -> float:
        """Return the planned mission duration."""

        return max(
            execution_event.event.end_time
            for execution_event in self.events
        )

    @property
    def event_count(self) -> int:
        """Return the number of executable events."""

        return len(self.events)

    @property
    def burn_count(self) -> int:
        """Return the number of executable burns."""

        return sum(
            execution_event.event.event_type
            == MissionEventType.BURN
            for execution_event in self.events
        )

    @property
    def coast_count(self) -> int:
        """Return the number of executable coast events."""

        return sum(
            execution_event.event.event_type
            == MissionEventType.COAST
            for execution_event in self.events
        )


@dataclass(frozen=True)
class ExecutedMissionEvent:
    """Result of executing one mission event."""

    name: str
    event_type: MissionEventType
    start_time: float
    end_time: float
    initial_mass: float
    final_mass: float
    propellant_consumed: float


@dataclass(frozen=True)
class MissionExecutionResult:
    """Complete result of executing a spacecraft mission."""

    initial_state: State3DThrust
    final_state: State3DThrust
    history: TrajectoryHistory
    events: tuple[ExecutedMissionEvent, ...]
    include_j2: bool

    @property
    def duration(self) -> float:
        """Return total executed mission duration."""

        return self.history.final_time

    @property
    def event_count(self) -> int:
        """Return number of executed events."""

        return len(self.events)

    @property
    def total_propellant_consumed(self) -> float:
        """Return total propellant consumed by the mission."""

        return (
            self.initial_state.mass
            - self.final_state.mass
        )

    @property
    def final_mass(self) -> float:
        """Return final spacecraft mass."""

        return self.final_state.mass


def _coast_model() -> ThrustModel:
    """Return a zero-thrust model for coast propagation."""

    return ThrustModel(
        thrust=0.0,
        specific_impulse=1.0,
    )


def _propagate_segment(
    initial_state: State3DThrust,
    duration: float,
    timestep: float,
    thrust_model: ThrustModel,
    burn_direction: BurnVector,
    dry_mass: float | None,
    include_j2: bool,
) -> TrajectoryHistory:
    """Propagate one continuous mission segment."""

    if include_j2:
        return simulate_trajectory_j2(
            initial_state=initial_state,
            duration=duration,
            timestep=timestep,
            thrust_model=thrust_model,
            thrust_direction=burn_direction,
            dry_mass=dry_mass,
        )

    return simulate_trajectory(
        initial_state=initial_state,
        duration=duration,
        timestep=timestep,
        thrust_model=thrust_model,
        thrust_direction=burn_direction,
        dry_mass=dry_mass,
    )


def _translate_history(
    history: TrajectoryHistory,
    start_time: float,
    include_initial: bool,
) -> list[TrajectoryPoint]:
    """Translate local segment times into absolute mission times."""

    points = history.points

    if not include_initial:
        points = points[1:]

    return [
        TrajectoryPoint(
            time=start_time + point.time,
            state=point.state,
        )
        for point in points
    ]


def _execute_coast(
    initial_state: State3DThrust,
    duration: float,
    timestep: float,
    include_j2: bool,
) -> TrajectoryHistory:
    """Execute a zero-thrust coast segment."""

    return _propagate_segment(
        initial_state=initial_state,
        duration=duration,
        timestep=timestep,
        thrust_model=_coast_model(),
        burn_direction=BurnVector(
            1.0,
            0.0,
            0.0,
        ),
        dry_mass=initial_state.mass,
        include_j2=include_j2,
    )


def create_mission_execution_plan(
    events: list[MissionExecutionEvent],
) -> MissionExecutionPlan:
    """Create a validated executable mission plan."""

    if not events:
        raise ValueError(
            "Mission execution plan cannot be empty."
        )

    return MissionExecutionPlan(
        events=tuple(events),
    )


def create_execution_plan_from_timeline(
    timeline: MissionTimeline,
    configurations: dict[
        str,
        MissionExecutionEvent,
    ],
) -> MissionExecutionPlan:
    """Attach execution configurations to an existing timeline."""

    if not timeline.events:
        raise ValueError(
            "Mission timeline cannot be empty."
        )

    execution_events: list[MissionExecutionEvent] = []

    for event in timeline.events:
        configuration = configurations.get(event.name)

        if configuration is None:
            if event.event_type == MissionEventType.COAST:
                configuration = MissionExecutionEvent(
                    event=event,
                )
            else:
                raise ValueError(
                    f"Missing execution configuration for "
                    f"burn event '{event.name}'."
                )

        if configuration.event != event:
            raise ValueError(
                f"Execution configuration does not match "
                f"timeline event '{event.name}'."
            )

        execution_events.append(configuration)

    return create_mission_execution_plan(
        execution_events
    )


def execute_mission(
    initial_state: State3DThrust,
    plan: MissionExecutionPlan,
    timestep: float = 1.0,
    include_j2: bool = False,
) -> MissionExecutionResult:
    """Execute a complete mission plan through the numerical physics engine.

    Events are executed in chronological order. Gaps between explicitly
    scheduled events are automatically treated as coast periods.

    Burn events use their configured finite-thrust model and direction.
    Coast events use zero thrust while spacecraft dynamics continue under
    gravity, with optional J2 perturbation.

    The returned trajectory history uses absolute mission time.
    """

    if initial_state.mass <= 0:
        raise ValueError(
            "Initial spacecraft mass must be greater than zero."
        )

    if timestep <= 0:
        raise ValueError(
            "Mission timestep must be greater than zero."
        )

    current_state = initial_state
    current_time = 0.0

    all_points: list[TrajectoryPoint] = [
        TrajectoryPoint(
            time=0.0,
            state=current_state,
        )
    ]

    executed_events: list[ExecutedMissionEvent] = []

    for execution_event in plan.events:
        event = execution_event.event

        if event.start_time > current_time:
            gap_duration = (
                event.start_time
                - current_time
            )

            coast_history = _execute_coast(
                initial_state=current_state,
                duration=gap_duration,
                timestep=timestep,
                include_j2=include_j2,
            )

            all_points.extend(
                _translate_history(
                    coast_history,
                    start_time=current_time,
                    include_initial=False,
                )
            )

            current_state = coast_history.final_state
            current_time = event.start_time

        event_initial_mass = current_state.mass

        if event.event_type == MissionEventType.BURN:
            if (
                execution_event.thrust_model is None
                or execution_event.burn_direction is None
                or execution_event.dry_mass is None
            ):
                raise ValueError(
                    f"Burn event '{event.name}' "
                    "is missing execution parameters."
                )

            segment_history = _propagate_segment(
                initial_state=current_state,
                duration=event.duration,
                timestep=timestep,
                thrust_model=execution_event.thrust_model,
                burn_direction=execution_event.burn_direction,
                dry_mass=execution_event.dry_mass,
                include_j2=include_j2,
            )

        else:
            segment_history = _execute_coast(
                initial_state=current_state,
                duration=event.duration,
                timestep=timestep,
                include_j2=include_j2,
            )

        all_points.extend(
            _translate_history(
                segment_history,
                start_time=event.start_time,
                include_initial=False,
            )
        )

        current_state = segment_history.final_state
        current_time = event.end_time

        executed_events.append(
            ExecutedMissionEvent(
                name=event.name,
                event_type=event.event_type,
                start_time=event.start_time,
                end_time=event.end_time,
                initial_mass=event_initial_mass,
                final_mass=current_state.mass,
                propellant_consumed=(
                    event_initial_mass
                    - current_state.mass
                ),
            )
        )

    history = TrajectoryHistory(
        points=tuple(all_points),
        timestep=timestep,
        duration=current_time,
        include_j2=include_j2,
    )

    return MissionExecutionResult(
        initial_state=initial_state,
        final_state=current_state,
        history=history,
        events=tuple(executed_events),
        include_j2=include_j2,
    )
