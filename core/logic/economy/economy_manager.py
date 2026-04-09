from __future__ import annotations

from core.models.entities import CharacterEntity


class EconomyManager:
    def liquidity_pressure(self, entity: CharacterEntity) -> float:
        return round(max(0.0, 60.0 - entity.status.financial_level), 4)
