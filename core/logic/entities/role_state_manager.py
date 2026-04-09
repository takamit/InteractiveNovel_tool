from __future__ import annotations

from core.models.entities import CharacterEntity


class RoleStateManager:
    def describe_role_pressure(self, entity: CharacterEntity) -> dict[str, float | str]:
        role_weight = {
            'protagonist': 0.95,
            'heroine': 0.88,
            'rival': 0.91,
            'observer': 0.70,
        }
        pressure = role_weight.get(entity.role.primary, 0.62) * (entity.status.stress + entity.status.rumor_level) / 2.0
        return {
            'role': entity.role.primary,
            'archetype': entity.role.archetype,
            'role_pressure': round(pressure, 4),
        }
