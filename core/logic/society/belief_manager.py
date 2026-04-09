from __future__ import annotations

from core.models.entities import CharacterEntity


class BeliefManager:
    def ideological_vector(self, entity: CharacterEntity) -> set[str]:
        return {value.lower() for value in entity.ideology.core_values}
