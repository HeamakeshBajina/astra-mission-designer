import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from astra.validation.sensitivity_analysis import run_sensitivity_analysis
from astra.validation.sensitivity_report import (
    sensitivity_report_to_json,
    sensitivity_report_to_markdown,
)

def main():
    output_dir = PROJECT_ROOT / "reports" / "sensitivity"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = run_sensitivity_analysis()
    md_path = output_dir / "orbital_sensitivity_report.md"
    json_path = output_dir / "orbital_sensitivity_report.json"

    md_path.write_text(
        sensitivity_report_to_markdown(results), encoding="utf-8"
    )
    json_path.write_text(
        sensitivity_report_to_json(results) + "\n", encoding="utf-8"
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert len(payload["results"]) == len(results), "Result count mismatch"
    print(f"Results analysed: {len(results)}")
    print(f"Ranked metrics: {len(payload['rankings'])}")
    print(f"Markdown report: {md_path.relative_to(PROJECT_ROOT)}")
    print(f"JSON report: {json_path.relative_to(PROJECT_ROOT)}")
    print("JSON validation: passed")

if __name__ == "__main__":
    main()
