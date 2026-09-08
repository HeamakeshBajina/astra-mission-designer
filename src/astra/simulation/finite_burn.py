"""Finite-duration spacecraft burn model for ASTRA."""

from dataclasses import dataclass

from astra.physics.thrust import ThrustModel


@dataclass(frozen=True)
class FiniteBurn:
    """A finite-duration constant-thrust burn."""

    thrust_model: ThrustModel
    duration: float
    dry_mass: float

    def __post_init__(self) -> None:
        """Validate burn parameters."""

        if self.duration < 0:
            raise ValueError(
                "Burn duration cannot be negative."
            )

        if self.dry_mass <= 0:
            raise ValueError(
                "Dry mass must be greater than zero."
            )

    @property
    def propellant_required(self) -> float:
        """Return propellant required for the complete burn."""

        return self.thrust_model.propellant_consumed(
            self.duration
        )

    def final_mass(self, initial_mass: float) -> float:
        """Return spacecraft mass after completing the burn."""

        if initial_mass <= 0:
            raise ValueError(
                "Initial mass must be greater than zero."
            )

        if initial_mass < self.dry_mass:
            raise ValueError(
                "Initial mass cannot be less than dry mass."
            )

        propellant_available = (
            initial_mass - self.dry_mass
        )

        if self.propellant_required > propellant_available:
            raise ValueError(
                "Burn requires more propellant than is available."
            )

        return (
            initial_mass -
            self.propellant_required
        )

    def can_complete(self, initial_mass: float) -> bool:
        """Return whether the burn can complete with available propellant."""

        return (
            self.final_mass(initial_mass)
            >= self.dry_mass
        )
