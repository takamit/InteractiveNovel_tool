from __future__ import annotations

from core.models.entities import RelationRecord


class RelationUnlockManager:
    def unlocked_layers(self, relation: RelationRecord) -> list[str]:
        layers = ['basic']
        if relation.basic.trust + relation.extended.interest >= 70:
            layers.append('extended')
        if relation.extended.attachment + relation.advanced.obsession >= 90:
            layers.append('advanced')
        return layers
