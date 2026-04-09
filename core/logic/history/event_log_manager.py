from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class EventLogManager:
    def recent(self, state: WorldState, limit: int = 20) -> list[dict[str, object]]:
        return list(state.event_log[-limit:])
