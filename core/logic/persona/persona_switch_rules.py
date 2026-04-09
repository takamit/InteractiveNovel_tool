from __future__ import annotations

from core.models.entities import CharacterEntity
from core.logic.persona.mask_detection import MaskDetectionEngine


class PersonaSwitchRules:
    def __init__(self) -> None:
        self.mask_engine = MaskDetectionEngine()

    def active_persona(self, entity: CharacterEntity) -> str:
        pressure = self.mask_engine.reveal_pressure(entity)
        if pressure >= entity.persona.switch_threshold:
            return entity.persona.hidden_persona
        return entity.persona.surface_persona
