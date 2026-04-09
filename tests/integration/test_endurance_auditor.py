from pathlib import Path

from core.logic.application import create_app
from core.logic.quality.diagnostics import ReleaseDiagnostics


def test_turn_traces_are_recorded_and_exposed() -> None:
    project_root = Path(__file__).resolve().parents[2]
    app = create_app(project_root)
    app.run_turns(turns=3, autosave=False)

    report = app.analysis()
    traces = report['recent_turn_traces']

    assert traces
    assert traces[-1]['turn'] == 3
    assert traces[-1]['action_chain']


def test_endurance_report_has_recommendations_shape() -> None:
    project_root = Path(__file__).resolve().parents[2]
    app = create_app(project_root)
    snapshots = []
    diagnostics = ReleaseDiagnostics()

    for _ in range(6):
        app.run_turns(turns=1, autosave=False)
        release_report = diagnostics.build_report(app.engine._ensure_state())
        metrics = dict(release_report['metrics'])
        metrics['turn'] = release_report['turn']
        metrics['release_score'] = release_report['release_score']
        snapshots.append(metrics)

    report = app.endurance_report(snapshots)

    assert 'stability_score' in report
    assert 'volatility' in report
    assert 'pressure_peaks' in report
    assert isinstance(report['recommendations'], list)
