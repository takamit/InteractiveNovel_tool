from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class HistoryViewRenderer:
    def render(self, state: WorldState, limit: int = 5) -> str:
        entries = state.event_log[-limit:]
        return '
'.join(entry.get('summary', entry.get('action_type', 'event')) for entry in entries)
