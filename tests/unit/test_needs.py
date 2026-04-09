from pathlib import Path

from core.logic.needs.priority_engine import NeedPriorityEngine
from core.services.persistence.json_loader import WorldDataLoader


def test_need_priority_engine_orders_values() -> None:
    project_root = Path(__file__).resolve().parents[2]
    entity = WorldDataLoader(project_root).load_world_models('sample_world')['entities'].entities[0]
    ranked = NeedPriorityEngine().rank(entity)
    assert ranked
    assert ranked[0][1] >= ranked[-1][1]
