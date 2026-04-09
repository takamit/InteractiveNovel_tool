from pathlib import Path

from core.services.persistence.json_loader import WorldDataLoader
from core.logic.relations.relation_trends import RelationTrendAnalyzer


def test_relation_trend_analyzer_returns_string() -> None:
    project_root = Path(__file__).resolve().parents[2]
    relation = WorldDataLoader(project_root).load_world_models('sample_world')['relations'].relations[0]
    assert isinstance(RelationTrendAnalyzer().infer(relation), str)
