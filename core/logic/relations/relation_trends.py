from __future__ import annotations

from core.models.entities import RelationRecord


class RelationTrendAnalyzer:
    def infer(self, relation: RelationRecord) -> str:
        positive = relation.basic.trust + relation.extended.intimacy + relation.advanced.devotion
        negative = relation.basic.suspicion + relation.advanced.resentment + relation.basic.fear
        if positive - negative >= 40:
            return 'warming'
        if negative - positive >= 40:
            return 'deteriorating'
        return 'stagnant'
