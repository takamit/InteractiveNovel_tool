from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class ContextCompiler:
    def compile(self, state: WorldState) -> dict[str, object]:
        return {
            'world_id': state.world_id,
            'turn': state.turn,
            'entity_count': len(state.entities),
            'revealed_secret_count': len(state.revealed_secrets),
        }
