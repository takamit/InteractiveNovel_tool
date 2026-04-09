from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class RegionalHistoryManager:
    def hottest_locations(self, state: WorldState, limit: int = 5) -> list[tuple[str, float]]:
        ranked = sorted(state.location_heat.items(), key=lambda item: item[1], reverse=True)
        return [(location_id, round(value, 4)) for location_id, value in ranked[:limit]]
