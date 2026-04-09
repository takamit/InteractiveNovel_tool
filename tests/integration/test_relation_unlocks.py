from pathlib import Path

from core.services.persistence.json_loader import WorldDataLoader
from core.logic.relations.relation_unlocks import RelationUnlockManager


def test_relation_unlock_manager_returns_basic() -> None:
    project_root = Path(__file__).resolve().parents[2]
    relation = WorldDataLoader(project_root).load_world_models('sample_world')['relations'].relations[0]
    unlocked = RelationUnlockManager().unlocked_layers(relation)
    assert 'basic' in unlocked
