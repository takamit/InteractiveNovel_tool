from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class HistoryManager:
    def summarize(self, state: WorldState) -> dict[str, object]:
        return {
            'turn': state.turn,
            'event_count': len(state.event_log),
            'revealed_secret_count': len(state.revealed_secrets),
            'offscreen_event_count': len(state.offscreen_events),
        }
