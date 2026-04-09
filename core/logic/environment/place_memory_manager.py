from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class PlaceMemoryManager:
    def remember(self, state: WorldState, location_id: str, note: str) -> None:
        state.location_pressure_history.append({'turn': state.turn, 'location_id': location_id, 'note': note})
