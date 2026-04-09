from __future__ import annotations


class CooldownManager:
    def __init__(self) -> None:
        self._cooldowns: dict[tuple[str, str], int] = {}

    def tick(self) -> None:
        next_state: dict[tuple[str, str], int] = {}
        for key, remaining in self._cooldowns.items():
            if remaining > 1:
                next_state[key] = remaining - 1
        self._cooldowns = next_state

    def set_cooldown(self, entity_id: str, action_type: str, turns: int) -> None:
        self._cooldowns[(entity_id, action_type)] = max(0, turns)

    def is_blocked(self, entity_id: str, action_type: str) -> bool:
        return self._cooldowns.get((entity_id, action_type), 0) > 0
