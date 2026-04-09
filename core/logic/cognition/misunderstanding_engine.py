from __future__ import annotations


class MisunderstandingEngine:
    def confusion_risk(self, readability: float, rumor_level: float, stress: float) -> float:
        risk = max(0.0, 60.0 - readability) * 0.6 + rumor_level * 0.2 + stress * 0.2
        return round(min(100.0, risk), 4)
