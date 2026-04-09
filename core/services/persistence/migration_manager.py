from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.logic.runtime.constants import SNAPSHOT_VERSION


class MigrationManager:
    def migrate_snapshot_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = deepcopy(payload)
        version = int(data.get('snapshot_version', 1))
        if version < 2:
            data.setdefault('relation_memories', {})
            data.setdefault('secret_pressure', {})
            data.setdefault('save_metadata', {})
            meta = data['save_metadata']
            meta.setdefault('slot_name', 'migrated')
            meta.setdefault('saved_turn', int(data.get('turn', 0)))
            meta.setdefault('summary', {})
            data['snapshot_version'] = 2
            version = 2
        if version < 3:
            data.setdefault('world_tension', 0.0)
            data.setdefault('location_heat', {})
            data.setdefault('location_pressure_history', [])
            data['snapshot_version'] = 3
            version = 3
        if version < 4:
            data.setdefault('faction_climate', {})
            data.setdefault('institution_pressure', 0.0)
            data.setdefault('reputation_pressure_log', [])
            data.setdefault('offscreen_events', [])
            data['snapshot_version'] = 4
            version = 4
        if version < 5:
            data.setdefault('turn_traces', [])
            data['snapshot_version'] = 5
            version = 5
        data['snapshot_version'] = SNAPSHOT_VERSION if version <= SNAPSHOT_VERSION else version
        return data
