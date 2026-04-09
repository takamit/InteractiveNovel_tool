from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class TimelineManager:
    def checkpoint(self, state: WorldState) -> dict[str, object]:
        return {
            'turn': state.turn,
            'highlights': [entry.get('summary') or entry.get('action_type') for entry in state.event_log[-5:]],
        }
