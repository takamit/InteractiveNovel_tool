from __future__ import annotations


class RelationDecayCalculator:
    def score(self, maintenance: float, decay: float) -> float:
        return round(max(0.0, decay + max(0.0, 45.0 - maintenance) * 0.05), 4)
