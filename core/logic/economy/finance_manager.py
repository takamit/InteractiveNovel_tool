from __future__ import annotations

from core.models.entities import CharacterEntity


class FinanceManager:
    def apply_cost(self, entity: CharacterEntity, cost: float) -> None:
        entity.status.financial_level = round(max(0.0, entity.status.financial_level - cost), 4)
