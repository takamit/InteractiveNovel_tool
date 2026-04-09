from core.logic.entities.entity_factory import CharacterEntityFactory
from core.services.persistence.json_loader import WorldDataLoader
from pathlib import Path


def test_character_entity_factory_creates_copy() -> None:
    project_root = Path(__file__).resolve().parents[2]
    loader = WorldDataLoader(project_root)
    models = loader.load_world_models('sample_world')
    entity = models['entities'].entities[0]
    clone = CharacterEntityFactory().create(entity)
    assert clone is not entity
    assert clone.id == entity.id
