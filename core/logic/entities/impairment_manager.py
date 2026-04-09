from __future__ import annotations

from core.models.entities import CharacterEntity


class ImpairmentManager:
    def action_penalty(self, entity: CharacterEntity) -> float:
        penalty = entity.status.injury * 0.35 + entity.status.fatigue * 0.18 + max(0.0, entity.status.stress - 55.0) * 0.12
        return round(penalty, 4)
