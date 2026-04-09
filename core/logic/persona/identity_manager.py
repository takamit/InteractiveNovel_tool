from __future__ import annotations

from core.models.entities import CharacterEntity


class IdentityManager:
    def summarize(self, entity: CharacterEntity) -> dict[str, str | float]:
        return {
            'entity_id': entity.id,
            'surface_persona': entity.persona.surface_persona,
            'hidden_persona': entity.persona.hidden_persona,
            'mask_strength': round(entity.persona.mask_strength, 4),
        }
