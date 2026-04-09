from __future__ import annotations


class EventConditionEvaluator:
    def threshold(self, value: float, minimum: float) -> bool:
        return value >= minimum
