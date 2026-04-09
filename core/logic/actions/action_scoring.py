from __future__ import annotations

from core.logic.actions.action_models import ActionCandidate


class ActionScoringEngine:
    def score(self, candidate: ActionCandidate, *, short_term: float, long_term: float, world_cost: float, bias: float = 0.0) -> ActionCandidate:
        candidate.score = round(short_term * 0.62 + long_term * 0.28 - world_cost + bias, 4)
        candidate.metadata.update({
            'short_term': round(short_term, 4),
            'long_term': round(long_term, 4),
            'world_cost': round(world_cost, 4),
            'bias': round(bias, 4),
        })
        return candidate
