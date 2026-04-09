from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class SocialTrendManager:
    def summarize(self, state: WorldState) -> dict[str, float]:
        average_rumor = sum(entity.status.rumor_level for entity in state.entities.values()) / max(1, len(state.entities))
        return {'average_rumor': round(average_rumor, 4), 'world_tension': round(state.world_tension, 4)}
