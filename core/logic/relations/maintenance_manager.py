from __future__ import annotations

from core.models.entities import RelationRecord


class RelationMaintenanceManager:
    def maintenance_pressure(self, relation: RelationRecord) -> float:
        return round(max(0.0, relation.decay - relation.maintenance * 0.35), 4)
