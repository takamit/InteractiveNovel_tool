from __future__ import annotations


class WeatherManager:
    def current_weather(self, turn: int) -> str:
        return 'clear' if turn % 4 != 0 else 'overcast'
