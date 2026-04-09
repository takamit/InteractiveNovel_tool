from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class PromptContextBuilder:
    def build_summary(self, state: WorldState) -> str:
        return f'world={state.world_id} turn={state.turn} tension={state.world_tension:.4f}'
