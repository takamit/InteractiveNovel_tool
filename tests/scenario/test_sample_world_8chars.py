from pathlib import Path

from core.services.persistence.json_loader import WorldDataLoader


def test_sample_world_has_eight_characters() -> None:
    project_root = Path(__file__).resolve().parents[2]
    models = WorldDataLoader(project_root).load_world_models('sample_world')
    assert len(models['entities'].entities) == 8
