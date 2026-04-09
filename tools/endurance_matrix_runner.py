from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.logic.application import create_app
from core.logic.quality.endurance_auditor import EnduranceAuditor
from core.logic.quality.diagnostics import ReleaseDiagnostics


def collect_snapshot(app) -> dict:
    report = ReleaseDiagnostics().build_report(app.engine._ensure_state())
    metrics = dict(report['metrics'])
    metrics['turn'] = report['turn']
    metrics['release_score'] = report['release_score']
    return metrics


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    app = create_app(project_root)
    per_turn: list[dict] = []
    checkpoints = [10, 25, 50]
    for target_turn in checkpoints:
        while app.engine._ensure_state().turn < target_turn:
            app.run_turns(turns=1, autosave=False)
            per_turn.append(collect_snapshot(app))

    auditor = EnduranceAuditor()
    report = auditor.build_report(per_turn, app.engine._ensure_state())

    payload = {
        'checkpoints': checkpoints,
        'per_turn_metrics': per_turn,
        'endurance_report': report,
    }

    output_dir = project_root / 'data' / 'exports' / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'endurance_matrix_report.json'
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(output_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
