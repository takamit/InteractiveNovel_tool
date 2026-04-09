from __future__ import annotations

from core.models.entities import CharacterEntity


class MotivationEngine:
    def score(self, entity: CharacterEntity) -> dict[str, float]:
        return {
            'affiliation': round(entity.needs.psychological.belonging * 0.55 + entity.emotions.affection * 0.45, 4),
            'avoidance': round(entity.needs.psychological.safety * 0.55 + entity.emotions.fear * 0.45, 4),
            'assertion': round(entity.needs.psychological.power * 0.60 + entity.emotions.anger * 0.40, 4),
            'restoration': round(entity.status.fatigue * 0.45 + entity.status.stress * 0.30 + entity.status.injury * 0.25, 4),
        }
