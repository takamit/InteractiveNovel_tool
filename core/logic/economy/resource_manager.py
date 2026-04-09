from __future__ import annotations


class ResourceManager:
    def ratio(self, current: float, maximum: float) -> float:
        if maximum <= 0:
            return 0.0
        return round(max(0.0, min(1.0, current / maximum)), 4)
