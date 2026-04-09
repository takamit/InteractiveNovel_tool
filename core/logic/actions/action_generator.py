from __future__ import annotations

from core.logic.actions.action_models import ActionCandidate


class ActionGenerator:
    DEFAULT_ACTIONS = ('observe', 'approach', 'support', 'withdraw', 'confront', 'confide', 'seek_help', 'wait')

    def generate(self, actor_id: str, *, target_id: str | None = None, location_id: str | None = None) -> list[ActionCandidate]:
        return [ActionCandidate(action_type=action_type, actor_id=actor_id, target_id=target_id, location_id=location_id) for action_type in self.DEFAULT_ACTIONS]
