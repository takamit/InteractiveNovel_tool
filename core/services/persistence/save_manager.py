from __future__ import annotations

import json
from pathlib import Path

from core.logic.runtime.world_state import WorldState
from core.models.entities import EntityFile, LocationFile, RelationFile, SecretFile
from core.services.persistence.migration_manager import MigrationManager
from core.services.persistence.snapshot_manager import SnapshotManager


class SaveManager:
    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root)
        self.snapshot_manager = SnapshotManager(project_root)
        self.migration_manager = MigrationManager()

    def save(self, state: WorldState, *, slot_name: str = 'slot_01') -> Path:
        return self.snapshot_manager.save_snapshot(state, slot_name=slot_name)

    def load(self, snapshot_path: str | Path) -> WorldState:
        path = Path(snapshot_path)
        payload = json.loads(path.read_text(encoding='utf-8'))
        payload = self.migration_manager.migrate_snapshot_payload(payload)

        entity_file = EntityFile.model_validate({'world_id': payload['world_id'], 'entities': payload['entities']})
        relation_file = RelationFile.model_validate({'world_id': payload['world_id'], 'relations': payload['relations']})
        secret_file = SecretFile.model_validate({'world_id': payload['world_id'], 'secrets': payload['secrets']})
        location_file = LocationFile.model_validate({'world_id': payload['world_id'], 'locations': payload['locations']})

        return WorldState.from_models(
            entities=entity_file,
            relations=relation_file,
            secrets=secret_file,
            locations=location_file,
            turn=int(payload.get('turn', 0)),
            event_log=list(payload.get('event_log', [])),
            last_actions=list(payload.get('last_actions', [])),
            revealed_secrets=list(payload.get('revealed_secrets', [])),
            secondary_events=list(payload.get('secondary_events', [])),
            relation_memories=dict(payload.get('relation_memories', {})),
            secret_pressure=dict(payload.get('secret_pressure', {})),
            world_tension=float(payload.get('world_tension', 0.0)),
            location_heat=dict(payload.get('location_heat', {})),
            location_pressure_history=list(payload.get('location_pressure_history', [])),
            save_metadata=dict(payload.get('save_metadata', {})),
            faction_climate=dict(payload.get('faction_climate', {})),
            institution_pressure=float(payload.get('institution_pressure', 0.0)),
            reputation_pressure_log=list(payload.get('reputation_pressure_log', [])),
            offscreen_events=list(payload.get('offscreen_events', [])),
            turn_traces=list(payload.get('turn_traces', [])),
        )
