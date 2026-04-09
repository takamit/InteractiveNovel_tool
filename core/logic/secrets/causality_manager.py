from __future__ import annotations


class CausalityManager:
    def chain(self, trigger: str, effects: list[str]) -> dict[str, object]:
        return {'trigger': trigger, 'effects': list(effects)}
