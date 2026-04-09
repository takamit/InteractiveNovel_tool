from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class AnalysisRenderer:
    def render(self, state: WorldState) -> str:
        return f'turn={state.turn} world_tension={state.world_tension:.4f} institution_pressure={state.institution_pressure:.4f}'
