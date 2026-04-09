from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from pydantic import ValidationError as PydanticValidationError

from core.logic.runtime.exceptions import WorldDataLoadError
from core.models.entities import EntityFile, LocationFile, RelationFile, SecretFile
from core.utils.logger import get_logger
from core.utils.validators import (
    collect_entity_ids,
    collect_referenced_location_ids,
    validate_entity_logic,
    validate_location_logic,
    validate_relation_logic,
    validate_secret_logic,
)

LOGGER = get_logger(__name__)


class WorldDataLoader:
    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root)
        self.schemas_dir = self.project_root / "schemas"
        self.worlds_dir = self.project_root / "data" / "worlds"

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise WorldDataLoadError(f"JSON file not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise WorldDataLoadError(f"Invalid JSON syntax in {path}: {exc}") from exc

    def _read_schema(self, schema_name: str) -> dict[str, Any]:
        schema_path = self.schemas_dir / schema_name
        try:
            return json.loads(schema_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise WorldDataLoadError(f"Schema file not found: {schema_path}") from exc
        except json.JSONDecodeError as exc:
            raise WorldDataLoadError(f"Invalid schema JSON in {schema_path}: {exc}") from exc

    def _validate_against_schema(self, data: dict[str, Any], schema_name: str) -> None:
        schema = self._read_schema(schema_name)
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
        if errors:
            lines = []
            for err in errors:
                path = ".".join(str(part) for part in err.absolute_path) or "<root>"
                lines.append(f"{schema_name} :: {path} :: {err.message}")
            raise WorldDataLoadError("\n".join(lines))

    def load_world_raw(self, world_name: str) -> dict[str, dict[str, Any]]:
        world_dir = self.worlds_dir / world_name
        files = {
            "entities": "entities.json",
            "relations": "relations.json",
            "secrets": "secrets.json",
            "locations": "locations.json",
        }
        payload = {key: self._read_json(world_dir / filename) for key, filename in files.items()}
        LOGGER.info("Loaded raw world payload for %s", world_name)
        return payload

    def validate_world(self, world_name: str) -> None:
        raw = self.load_world_raw(world_name)
        self._validate_against_schema(raw["entities"], "entity.schema.json")
        self._validate_against_schema(raw["relations"], "relation.schema.json")
        self._validate_against_schema(raw["secrets"], "secret.schema.json")
        self._validate_against_schema(raw["locations"], "location.schema.json")

        errors: list[str] = []
        errors.extend(validate_entity_logic(raw["entities"]))

        entity_ids = collect_entity_ids(raw["entities"])
        referenced_location_ids = collect_referenced_location_ids(raw["entities"])

        errors.extend(validate_relation_logic(raw["relations"], entity_ids))
        errors.extend(validate_secret_logic(raw["secrets"], entity_ids))
        errors.extend(validate_location_logic(raw["locations"], referenced_location_ids))

        if errors:
            raise WorldDataLoadError("\n".join(errors))
        LOGGER.info("Validation passed for world=%s", world_name)

    def load_world_models(self, world_name: str) -> dict[str, Any]:
        self.validate_world(world_name)
        raw = self.load_world_raw(world_name)
        try:
            models = {
                "entities": EntityFile.model_validate(raw["entities"]),
                "relations": RelationFile.model_validate(raw["relations"]),
                "secrets": SecretFile.model_validate(raw["secrets"]),
                "locations": LocationFile.model_validate(raw["locations"]),
            }
            LOGGER.info("Pydantic model validation passed for world=%s", world_name)
            return models
        except PydanticValidationError as exc:
            raise WorldDataLoadError(str(exc)) from exc


JsonLoader = WorldDataLoader


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    loader = WorldDataLoader(project_root)
    models = loader.load_world_models("sample_world")
    print("Loaded successfully:")
    print(f"  entities : {len(models['entities'].entities)}")
    print(f"  relations: {len(models['relations'].relations)}")
    print(f"  secrets  : {len(models['secrets'].secrets)}")
    print(f"  locations: {len(models['locations'].locations)}")
