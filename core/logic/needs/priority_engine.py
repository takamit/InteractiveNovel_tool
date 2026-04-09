from __future__ import annotations

from core.logic.runtime.constants import NEED_PRIORITY_WEIGHTS
from core.models.entities import CharacterEntity


class NeedPriorityEngine:
    def rank(self, entity: CharacterEntity) -> list[tuple[str, float]]:
        values = {
            'hunger': entity.needs.survival.hunger,
            'thirst': entity.needs.survival.thirst,
            'sleepiness': entity.needs.survival.sleepiness,
            'health': 100.0 - entity.needs.survival.health,
            'sexual_desire': entity.needs.reproduction.sexual_desire,
            'intimacy': entity.needs.reproduction.intimacy,
            'belonging': entity.needs.psychological.belonging,
            'approval': entity.needs.psychological.approval,
            'safety': entity.needs.psychological.safety,
            'power': entity.needs.psychological.power,
            'freedom': entity.needs.psychological.freedom,
        }
        scored = [(key, round(value * NEED_PRIORITY_WEIGHTS[key], 4)) for key, value in values.items()]
        return sorted(scored, key=lambda item: item[1], reverse=True)
