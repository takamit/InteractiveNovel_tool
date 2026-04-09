from __future__ import annotations

from core.logic.runtime.constants import DEFAULT_NEED_DRIFT, MAX_VALUE, MIN_VALUE
from core.models.entities import CharacterEntity


class NeedStateManager:
    def advance_turn(self, entity: CharacterEntity) -> None:
        for group_name in ('survival', 'reproduction', 'psychological'):
            group = getattr(entity.needs, group_name)
            for key, drift in DEFAULT_NEED_DRIFT.items():
                if hasattr(group, key):
                    value = getattr(group, key)
                    setattr(group, key, round(max(MIN_VALUE, min(MAX_VALUE, value + drift)), 4))
