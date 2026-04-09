from __future__ import annotations

from core.logic.actions.action_models import ActionCandidate
from core.logic.actions.cooldown_manager import CooldownManager


class ActionValidator:
    def __init__(self, cooldown_manager: CooldownManager | None = None) -> None:
        self.cooldown_manager = cooldown_manager or CooldownManager()

    def validate(self, candidate: ActionCandidate) -> tuple[bool, str]:
        if self.cooldown_manager.is_blocked(candidate.actor_id, candidate.action_type):
            return False, 'cooldown_blocked'
        return True, 'ok'
