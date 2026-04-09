from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class RumorHistoryManager:
    def hottest_entities(self, state: WorldState, limit: int = 5) -> list[tuple[str, float]]:
        ranked = sorted(((entity.id, entity.status.rumor_level) for entity in state.entities.values()), key=lambda item: item[1], reverse=True)
        return [(entity_id, round(value, 4)) for entity_id, value in ranked[:limit]]
