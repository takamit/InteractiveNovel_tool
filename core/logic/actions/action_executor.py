from __future__ import annotations

from core.logic.actions.action_models import ActionCandidate


class ActionExecutor:
    def execute(self, candidate: ActionCandidate) -> dict[str, object]:
        return {
            'actor_id': candidate.actor_id,
            'target_id': candidate.target_id,
            'location_id': candidate.location_id,
            'action_type': candidate.action_type,
            'score': candidate.score,
            'metadata': dict(candidate.metadata),
        }
