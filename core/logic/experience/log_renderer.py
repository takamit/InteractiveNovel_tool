from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class LogRenderer:
    def render(self, state: WorldState, limit: int = 10) -> str:
        return '
'.join(str(item) for item in state.event_log[-limit:])
