from pathlib import Path

from core.logic.application import create_app
from ui.cli.main_cli import SimulationCliRunner, InteractiveCliRunner
from ui.desktop.app import SimulationDesktopRunner, InteractiveDesktopRunner


def test_release_report_has_expected_shape() -> None:
    project_root = Path(__file__).resolve().parents[2]
    app = create_app(project_root)
    app.run_turns(turns=5, autosave=False)
    report = app.release_report()

    assert "release_score" in report
    assert "release_ready" in report
    assert "warnings" in report
    assert "metrics" in report
    assert report["metrics"]["entity_count"] == 8


def test_runner_aliases_are_kept_for_compatibility() -> None:
    assert InteractiveCliRunner is SimulationCliRunner
    assert InteractiveDesktopRunner is SimulationDesktopRunner
