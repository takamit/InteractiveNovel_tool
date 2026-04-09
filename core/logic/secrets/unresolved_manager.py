from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class UnresolvedSecretManager:
    def list_unresolved(self, state: WorldState) -> list[str]:
        return [secret.id for secret in state.secrets.values() if secret.visibility != 'revealed']
