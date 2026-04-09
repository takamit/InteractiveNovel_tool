from pathlib import Path

from core.logic.runtime.engine import SimulationEngine


def test_revealed_secrets_log_is_list() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root)
    state = engine.bootstrap()
    assert isinstance(state.revealed_secrets, list)
