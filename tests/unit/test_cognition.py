from pathlib import Path

from core.logic.cognition.perception_engine import PerceptionEngine
from core.services.persistence.json_loader import WorldDataLoader


def test_perception_engine_returns_metrics() -> None:
    project_root = Path(__file__).resolve().parents[2]
    models = WorldDataLoader(project_root).load_world_models('sample_world')
    actor = models['entities'].entities[0]
    target = models['entities'].entities[1]
    location = models['locations'].locations[0]
    result = PerceptionEngine().perceive(actor, target, location)
    assert set(result) == {'proximity', 'readability', 'threat'}
