from __future__ import annotations

from core.models.entities import CharacterEntity


class CharacterConditionManager:
    def collect_conditions(self, entity: CharacterEntity) -> list[str]:
        conditions: list[str] = []
        if entity.status.stress >= 70:
            conditions.append('high_stress')
        if entity.status.fatigue >= 60:
            conditions.append('fatigued')
        if entity.status.injury >= 15:
            conditions.append('injured')
        if entity.status.rumor_level >= 60:
            conditions.append('under_rumor_pressure')
        if entity.needs.psychological.safety >= 70:
            conditions.append('safety_deprived')
        return conditions
