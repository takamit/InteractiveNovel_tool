from __future__ import annotations


class SeasonManager:
    def season_from_turn(self, turn: int) -> str:
        seasons = ('spring', 'summer', 'autumn', 'winter')
        return seasons[(max(0, turn - 1) // 25) % len(seasons)]
