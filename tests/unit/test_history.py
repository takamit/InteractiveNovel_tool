from pathlib import Path

from core.logic.runtime.engine import SimulationEngine
from core.logic.history.history_manager import HistoryManager


def test_history_manager_summarizes_state() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root)
    state = engine.bootstrap()
    summary = HistoryManager().summarize(state)
    assert summary['turn'] == 0
