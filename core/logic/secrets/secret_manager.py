from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class SecretManager:
    def visible_secrets(self, state: WorldState, minimum_visibility: str = 'rumored') -> list[str]:
        order = ['hidden', 'implied', 'rumored', 'revealed']
        threshold = order.index(minimum_visibility)
        return [secret.id for secret in state.secrets.values() if order.index(secret.visibility) >= threshold]
