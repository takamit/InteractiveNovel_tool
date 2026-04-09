from pathlib import Path

from core.logic.runtime.engine import SimulationEngine


def test_offscreen_events_list_exists_after_turn() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root)
    engine.bootstrap()
    engine.run_turn()
    assert isinstance(engine.state.offscreen_events, list)
