from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class EntityHistoryManager:
    def snapshots(self, state: WorldState, entity_id: str) -> dict[str, float | str]:
        entity = state.entities[entity_id]
        return {
            'entity_id': entity.id,
            'name': entity.name.full_name,
            'stress': round(entity.status.stress, 4),
            'rumor_level': round(entity.status.rumor_level, 4),
            'reputation': round(entity.status.visible_reputation, 4),
        }
