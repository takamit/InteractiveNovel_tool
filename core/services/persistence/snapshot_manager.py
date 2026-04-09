from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.logic.runtime.constants import SNAPSHOT_VERSION
from core.logic.runtime.world_state import WorldState
from core.services.persistence.json_saver import WorldDataWriter


class SnapshotManager:
    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root)
        self.saver = WorldDataWriter()

    def build_snapshot_payload(self, state: WorldState, *, slot_name: str = 'autosave') -> dict[str, Any]:
        summary = state.summary()
        save_metadata = {
            'slot_name': slot_name,
            'saved_turn': state.turn,
            'saved_at': datetime.now(timezone.utc).isoformat(),
            'summary': summary,
        }
        state.save_metadata = dict(save_metadata)
        return {
            'snapshot_version': SNAPSHOT_VERSION,
            'world_id': state.world_id,
            'turn': state.turn,
            'entities': [entity.model_dump(mode='json') for entity in state.entities.values()],
            'relations': [relation.model_dump(by_alias=True, mode='json') for relation in state.relations.values()],
            'secrets': [secret.model_dump(mode='json') for secret in state.secrets.values()],
            'locations': [location.model_dump(mode='json') for location in state.locations.values()],
            'event_log': list(state.event_log),
            'last_actions': list(state.last_actions),
            'revealed_secrets': list(state.revealed_secrets),
            'secondary_events': list(state.secondary_events),
            'relation_memories': {key: dict(value) for key, value in state.relation_memories.items()},
            'secret_pressure': {key: float(value) for key, value in state.secret_pressure.items()},
            'world_tension': float(state.world_tension),
            'location_heat': {key: float(value) for key, value in state.location_heat.items()},
            'location_pressure_history': list(state.location_pressure_history),
            'save_metadata': save_metadata,
            'faction_climate': {key: float(value) for key, value in state.faction_climate.items()},
            'institution_pressure': float(state.institution_pressure),
            'reputation_pressure_log': list(state.reputation_pressure_log),
            'offscreen_events': list(state.offscreen_events),
            'turn_traces': list(state.turn_traces),
        }

    def save_snapshot(self, state: WorldState, *, slot_name: str = 'autosave') -> Path:
        payload = self.build_snapshot_payload(state, slot_name=slot_name)
        snapshot_path = self.project_root / 'data' / 'saves' / slot_name / f'turn_{state.turn:04d}_snapshot.json'
        return self.saver.write_json(snapshot_path, payload)
