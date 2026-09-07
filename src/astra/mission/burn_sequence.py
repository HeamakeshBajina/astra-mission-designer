"""Multi-burn mission sequencing for ASTRA."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MissionBurn:
    """A planned spacecraft burn."""

    name: str
    time: float
    delta_v: float
    direction: str


@dataclass(frozen=True)
class BurnSequence:
    """An ordered sequence of spacecraft burns."""

    burns: list[MissionBurn]

    @property
    def total_delta_v(self) -> float:
        """Return the total magnitude of all planned burns."""
        return sum(burn.delta_v for burn in self.burns)

    @property
    def burn_count(self) -> int:
        """Return the number of burns in the sequence."""
        return len(self.burns)


def create_burn_sequence(
    burns: list[MissionBurn],
) -> BurnSequence:
    """Create and validate an ordered burn sequence."""
    if not burns:
        raise ValueError("Burn sequence cannot be empty.")

    previous_time = -1.0

    for burn in burns:
        if burn.time < 0:
            raise ValueError(
                "Burn time cannot be negative."
            )

        if burn.delta_v < 0:
            raise ValueError(
                "Burn delta-v cannot be negative."
            )

        if burn.time < previous_time:
            raise ValueError(
                "Burns must be ordered by time."
            )

        if not burn.name.strip():
            raise ValueError(
                "Burn name cannot be empty."
            )

        if not burn.direction.strip():
            raise ValueError(
                "Burn direction cannot be empty."
            )

        previous_time = burn.time

    return BurnSequence(
        burns=list(burns),
    )