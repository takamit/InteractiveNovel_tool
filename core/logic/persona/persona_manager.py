from __future__ import annotations

from core.models.entities import CharacterEntity
from core.logic.persona.persona_switch_rules import PersonaSwitchRules


class PersonaManager:
    def __init__(self) -> None:
        self.rules = PersonaSwitchRules()

    def resolve(self, entity: CharacterEntity) -> dict[str, str]:
        active = self.rules.active_persona(entity)
        return {'entity_id': entity.id, 'active_persona': active}
