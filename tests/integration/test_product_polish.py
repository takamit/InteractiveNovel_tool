from pathlib import Path

from core.logic.application import DialogueNovelApp, SimulationApplication
from core.logic.events.off_screen_events import OffScreenEventEngine, OffscreenEventEngine
from core.logic.experience.output_formatter import TurnViewRenderer, WorldViewRenderer
from core.services.persistence.json_loader import JsonLoader, WorldDataLoader
from core.logic.relations.relation_manager import RelationDynamics, RelationManager
from ui.cli.main_cli import CliApplication, InteractiveCliRunner


def test_standardized_class_aliases() -> None:
    assert JsonLoader is WorldDataLoader
    assert TurnViewRenderer is WorldViewRenderer
    assert RelationDynamics is RelationManager
    assert OffScreenEventEngine is OffscreenEventEngine
    assert DialogueNovelApp is SimulationApplication
    assert CliApplication is InteractiveCliRunner


def test_application_facade_runs_turns() -> None:
    project_root = Path(__file__).resolve().parents[2]
    app = SimulationApplication(project_root)
    app.bootstrap()
    results = app.run_turns(turns=2, autosave=False)
    assert len(results) == 2
    assert app.analysis()['turn'] == 2
    assert app.analysis()['player_ready'] is True
