from __future__ import annotations

from core.models.entities import CharacterEntity


class TabooManager:
    def taboo_hits(self, entity: CharacterEntity, tags: list[str]) -> int:
        taboos = {value.lower() for value in entity.ideology.taboo_values}
        return sum(1 for tag in tags if tag.lower() in taboos)
