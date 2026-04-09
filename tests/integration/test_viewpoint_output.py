from pathlib import Path

from core.logic.runtime.engine import SimulationEngine


def test_viewpoint_output_contains_turn_label() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root)
    engine.bootstrap()
    engine.run_turn()
    rendered = engine.render_latest_turn(mode='omniscient')
    assert 'TURN' in rendered
