"""Finite-duration thrust and mass-flow calculations for ASTRA."""

from dataclasses import dataclass

from astra.physics.constants import G0


@dataclass(frozen=True)
class ThrustModel:
    """Constant-thrust propulsion model."""

    thrust: float
    specific_impulse: float

    def __post_init__(self) -> None:
        """Validate the propulsion parameters."""

        if self.thrust < 0:
            raise ValueError(
                "Thrust cannot be negative."
            )

        if self.specific_impulse <= 0:
            raise ValueError(
                "Specific impulse must be greater than zero."
            )

    @property
    def mass_flow_rate(self) -> float:
        """Return propellant mass flow rate in kg/s.

        Uses:

            mdot = T / (Isp * g0)

        where:
            T   = thrust in newtons
            Isp = specific impulse in seconds
            g0  = standard gravitational acceleration.
        """

        return self.thrust / (
            self.specific_impulse * G0
        )

    def propellant_consumed(
        self,
        duration: float,
    ) -> float:
        """Return propellant consumed during a constant-thrust burn."""

        if duration < 0:
            raise ValueError(
                "Burn duration cannot be negative."
            )

        return self.mass_flow_rate * duration

    def remaining_mass(
        self,
        initial_mass: float,
        duration: float,
    ) -> float:
        """Return spacecraft mass after a finite-duration burn."""

        if initial_mass <= 0:
            raise ValueError(
                "Initial mass must be greater than zero."
            )

        consumed = self.propellant_consumed(
            duration
        )

        if consumed > initial_mass:
            raise ValueError(
                "Burn consumes more mass than is available."
            )

        return initial_mass - consumed
