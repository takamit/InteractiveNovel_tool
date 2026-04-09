from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class GlobalHistoryManager:
    def climate_snapshot(self, state: WorldState) -> dict[str, float]:
        return {
            'world_tension': round(state.world_tension, 4),
            'institution_pressure': round(state.institution_pressure, 4),
        }
