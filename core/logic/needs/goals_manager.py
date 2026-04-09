from __future__ import annotations

from core.models.entities import CharacterEntity


class GoalSelectionManager:
    def select_primary_goal(self, entity: CharacterEntity) -> str:
        goals = {
            'stabilize': entity.status.stress + entity.needs.psychological.safety,
            'connect': entity.needs.psychological.belonging + entity.needs.reproduction.intimacy,
            'advance_status': entity.needs.psychological.power + entity.status.rumor_level * 0.5,
            'recover': entity.status.fatigue + entity.status.injury + (100.0 - entity.needs.survival.health),
        }
        return max(goals.items(), key=lambda item: item[1])[0]
