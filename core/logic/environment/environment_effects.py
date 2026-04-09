from __future__ import annotations


class EnvironmentEffects:
    def privacy_bonus(self, privacy_level: float) -> float:
        return round(privacy_level * 0.08, 4)
