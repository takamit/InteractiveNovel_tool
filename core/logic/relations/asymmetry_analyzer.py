from __future__ import annotations

from core.models.entities import RelationRecord


class AsymmetryAnalyzer:
    def compare(self, forward: RelationRecord, reverse: RelationRecord) -> float:
        value = abs(forward.basic.like - reverse.basic.like) + abs(forward.basic.trust - reverse.basic.trust) + abs(forward.extended.attachment - reverse.extended.attachment)
        return round(value / 3.0, 4)
