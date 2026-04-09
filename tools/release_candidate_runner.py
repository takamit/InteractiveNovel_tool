from __future__ import annotations

import json
from pathlib import Path

from core.logic.application import create_app


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    app = create_app(project_root)
    app.run_turns(turns=25, autosave=False)
    report = app.release_report()

    report_dir = project_root / "data" / "exports" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    output_path = report_dir / "release_candidate_report.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
