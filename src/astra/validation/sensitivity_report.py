"""Reporting utilities for ASTRA orbital sensitivity analysis."""
from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from astra.validation.sensitivity_analysis import SensitivityResult


def build_sensitivity_report(results: Iterable[SensitivityResult]) -> dict[str, Any]:
    """Build a deterministic report ranked by observed relative change."""
    rows = list(results)
    if not rows:
        raise ValueError("At least one sensitivity result is required.")

    baselines: dict[str, float] = {}
    scores: dict[str, dict[str, float]] = defaultdict(dict)

    for row in rows:
        metric = row.metric
        baseline = float(row.baseline_value)
        if metric in baselines and baselines[metric] != baseline:
            raise ValueError(f"Inconsistent baseline values for {metric!r}.")
        baselines[metric] = baseline
        score = abs(float(row.relative_change_percent))
        scores[metric][row.parameter] = max(
            scores[metric].get(row.parameter, 0.0), score
        )

    rankings = {}
    for metric in sorted(scores):
        ordered = sorted(scores[metric].items(), key=lambda item: (-item[1], item[0]))
        rankings[metric] = [
            {
                "rank": index,
                "parameter": parameter,
                "max_absolute_relative_change_percent": score,
            }
            for index, (parameter, score) in enumerate(ordered, start=1)
        ]

    details = [
        {
            "parameter": row.parameter,
            "perturbation_percent": float(row.perturbation_percent),
            "metric": row.metric,
            "baseline_value": float(row.baseline_value),
            "perturbed_value": float(row.perturbed_value),
            "absolute_change": float(row.absolute_change),
            "relative_change_percent": float(row.relative_change_percent),
        }
        for row in rows
    ]
    details.sort(key=lambda item: (
        item["metric"], item["parameter"], item["perturbation_percent"]
    ))

    return {
        "report_name": "ASTRA Orbital Sensitivity Analysis",
        "method": "One-at-a-time parametric sensitivity analysis",
        "ranking_method": (
            "Rank by maximum absolute relative metric change across the "
            "supplied perturbations."
        ),
        "baseline_metrics": {key: baselines[key] for key in sorted(baselines)},
        "rankings": rankings,
        "results": details,
        "limitations": [
            "Rankings describe only the supplied perturbation cases.",
            "This is not probabilistic uncertainty propagation.",
            "Rankings depend on the baseline and perturbation range.",
            "Sensitivity alone does not establish engineering risk.",
        ],
    }


def sensitivity_report_to_json(
    results: Iterable[SensitivityResult], *, indent: int = 2
) -> str:
    """Serialize a report as JSON."""
    if isinstance(indent, bool) or not isinstance(indent, int) or indent < 0:
        raise ValueError("indent must be a non-negative integer.")
    return json.dumps(
        build_sensitivity_report(results),
        indent=indent,
        sort_keys=True,
        allow_nan=False,
    )


def sensitivity_report_to_markdown(results: Iterable[SensitivityResult]) -> str:
    """Render the report as Markdown."""
    report = build_sensitivity_report(results)
    lines = [
        f"# {report['report_name']}",
        "",
        f"**Method:** {report['method']}",
        "",
        report["ranking_method"],
        "",
        "## Baseline metrics",
        "",
        "| Metric | Baseline value |",
        "|---|---:|",
    ]
    for metric, value in report["baseline_metrics"].items():
        lines.append(f"| {metric} | {value:.10g} |")

    lines.extend(["", "## Sensitivity rankings", ""])
    for metric, ranked in report["rankings"].items():
        lines.extend([
            f"### {metric}", "",
            "| Rank | Parameter | Maximum absolute relative change (%) |",
            "|---:|---|---:|",
        ])
        for item in ranked:
            lines.append(
                f"| {item['rank']} | {item['parameter']} | "
                f"{item['max_absolute_relative_change_percent']:.8g} |"
            )
        lines.append("")

    lines.extend([
        "## Perturbation results", "",
        "| Metric | Parameter | Perturbation (%) | Baseline | Perturbed | "
        "Absolute change | Relative change (%) |",
        "|---|---|---:|---:|---:|---:|---:|",
    ])
    for item in report["results"]:
        lines.append(
            f"| {item['metric']} | {item['parameter']} | "
            f"{item['perturbation_percent']:.8g} | "
            f"{item['baseline_value']:.10g} | "
            f"{item['perturbed_value']:.10g} | "
            f"{item['absolute_change']:.10g} | "
            f"{item['relative_change_percent']:.8g} |"
        )

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    return "\n".join(lines)
