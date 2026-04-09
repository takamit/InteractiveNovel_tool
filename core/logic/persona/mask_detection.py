from __future__ import annotations

from core.models.entities import CharacterEntity


class MaskDetectionEngine:
    def reveal_pressure(self, entity: CharacterEntity) -> float:
        pressure = entity.status.stress * 0.45 + entity.inner_profile.loneliness * 0.20 + (100.0 - entity.persona.mask_strength) * 0.35
        return round(pressure, 4)
