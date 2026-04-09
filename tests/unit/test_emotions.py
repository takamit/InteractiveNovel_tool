from pathlib import Path

from core.logic.emotions.emotion_manager import EmotionStateManager
from core.services.persistence.json_loader import WorldDataLoader


def test_emotion_state_manager_returns_breakdown_info() -> None:
    project_root = Path(__file__).resolve().parents[2]
    entity = WorldDataLoader(project_root).load_world_models('sample_world')['entities'].entities[0]
    result = EmotionStateManager().advance_turn(entity)
    assert 'breakdown_risk' in result
