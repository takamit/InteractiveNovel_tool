from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.models.entities import CharacterEntity


class CharacterEntityFactory:
    """Creates safe copies of character models for runtime mutation."""

    def create(self, payload: CharacterEntity | dict[str, Any]) -> CharacterEntity:
        if isinstance(payload, CharacterEntity):
            return payload.model_copy(deep=True)
        return CharacterEntity.model_validate(deepcopy(payload))
