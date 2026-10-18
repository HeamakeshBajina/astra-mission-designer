"""Structured, deterministic mission validation reports for ASTRA."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
from typing import Any


class CheckStatus(str, Enum):
    """Outcome of an individual validation check."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_RUN = "NOT RUN"


@dataclass(frozen=True)
class ValidationCheck:
    """One validation result, including its evidence and limitations."""

    check_id: str
    name: str
    status: CheckStatus
    summary: str
    details: str = ""
    value: float | str | int | bool | None = None
    unit: str | None = None
    threshold: float | str | int | None = None

    def __post_init__(self) -> None:
        if not self.check_id.strip():
            raise ValueError("check_id cannot be empty.")
        if not self.name.strip():
            raise ValueError("Check name cannot be empty.")
        if not self.summary.strip():
            raise ValueError("Check summary cannot be empty.")
        if not isinstance(self.status, CheckStatus):
            raise TypeError("status must be a CheckStatus value.")


@dataclass(frozen=True)
class MissionValidationReport:
    """Portable mission-validation record with explicit assumptions."""

    mission_name: str
    created_at: str
    software_version: str
    checks: tuple[ValidationCheck, ...] = ()
    assumptions: tuple[str, ...] = ()
    inputs: dict[str, Any] = field(default_factory=dict)
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for label, value in (
            ("mission_name", self.mission_name),
            ("created_at", self.created_at),
            ("software_version", self.software_version),
        ):
            if not value.strip():
                raise ValueError(f"{label} cannot be empty.")

        ids = [check.check_id for check in self.checks]
        if len(ids) != len(set(ids)):
            raise ValueError("check_id values must be unique.")

        # Ensure report inputs can be represented as JSON.
        try:
            json.dumps(self.inputs, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "inputs must contain finite, JSON-serializable values."
            ) from exc

    @property
    def status(self) -> CheckStatus:
        """Summarize outcomes conservatively; this is not a safety certification."""
        statuses = {check.status for check in self.checks}

        if CheckStatus.FAIL in statuses:
            return CheckStatus.FAIL
        if CheckStatus.WARNING in statuses:
            return CheckStatus.WARNING
        if CheckStatus.NOT_RUN in statuses or not statuses:
            return CheckStatus.NOT_RUN
        return CheckStatus.PASS

    @property
    def summary_counts(self) -> dict[str, int]:
        """Count checks by status, including statuses with zero results."""
        return {
            status.value: sum(
                check.status is status for check in self.checks
            )
            for status in CheckStatus
        }

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation with stable field names."""
        return {
            "schema_version": "1.0",
            "mission_name": self.mission_name,
            "created_at": self.created_at,
            "software_version": self.software_version,
            "overall_status": self.status.value,
            "summary_counts": self.summary_counts,
            "assumptions": list(self.assumptions),
            "inputs": self.inputs,
            "notes": list(self.notes),
            "checks": [
                {
                    **asdict(check),
                    "status": check.status.value,
                }
                for check in self.checks
            ],
        }

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the report deterministically as JSON."""
        if indent < 0:
            raise ValueError("indent must be non-negative.")

        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        ) + "\n"

    def to_markdown(self) -> str:
        """Render a readable report without implying unperformed checks passed."""
        lines = [
            f"# Mission Validation Report: {self.mission_name}",
            "",
            f"- **Overall status:** {self.status.value}",
            f"- **Report timestamp:** {self.created_at}",
            f"- **ASTRA software version:** {self.software_version}",
            f"- **Checks recorded:** {len(self.checks)}",
            "",
            "## Check summary",
            "",
            "| Status | Count |",
            "|---|---:|",
        ]

        for status, count in self.summary_counts.items():
            lines.append(f"| {status} | {count} |")

        lines.extend(["", "## Validation checks", ""])

        if not self.checks:
            lines.append("No validation checks have been recorded.")
        else:
            for check in self.checks:
                lines.extend([
                    f"### {check.name}",
                    "",
                    f"- **ID:** `{check.check_id}`",
                    f"- **Status:** {check.status.value}",
                    f"- **Result:** {check.summary}",
                ])
                if check.value is not None:
                    value = f"{check.value}"
                    if check.unit:
                        value += f" {check.unit}"
                    lines.append(f"- **Value:** {value}")
                if check.threshold is not None:
                    lines.append(f"- **Threshold:** {check.threshold}")
                if check.details:
                    lines.append(f"- **Details:** {check.details}")
                lines.append("")

        lines.extend(["## Mission inputs", ""])
        if self.inputs:
            lines.extend([
                "```json",
                json.dumps(
                    self.inputs,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                    allow_nan=False,
                ),
                "```",
                "",
            ])
        else:
            lines.extend(["No mission inputs recorded.", ""])

        lines.extend(["## Assumptions", ""])
        if self.assumptions:
            lines.extend(f"- {item}" for item in self.assumptions)
        else:
            lines.append("No assumptions recorded.")
        lines.append("")

        lines.extend(["## Notes and limitations", ""])
        if self.notes:
            lines.extend(f"- {item}" for item in self.notes)
        else:
            lines.append("No additional notes recorded.")

        lines.extend([
            "",
            "---",
            "",
            "This report records the checks supplied to ASTRA. "
            "It is not, by itself, proof of mission feasibility, "
            "flight readiness, or spacecraft safety.",
            "",
        ])
        return "\n".join(lines)