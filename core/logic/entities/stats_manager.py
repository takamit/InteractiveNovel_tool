from __future__ import annotations

from core.models.entities import CharacterEntity


class CharacterStatsManager:
    def summarize(self, entity: CharacterEntity) -> dict[str, float | str]:
        vitality = max(0.0, entity.needs.survival.health - entity.status.fatigue * 0.45 - entity.status.injury * 0.85)
        social_capacity = max(0.0, entity.status.visible_reputation * 0.45 + entity.inner_profile.maturity * 0.25 + entity.needs.psychological.belonging * 0.15 - entity.status.stress * 0.30)
        volatility = max(0.0, entity.emotions.anger * 0.35 + entity.emotions.fear * 0.25 + entity.inner_profile.insecurity * 0.20 + entity.status.rumor_level * 0.20)
        return {
            'entity_id': entity.id,
            'vitality': round(vitality, 4),
            'social_capacity': round(social_capacity, 4),
            'volatility': round(volatility, 4),
        }
