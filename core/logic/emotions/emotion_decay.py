from __future__ import annotations

from core.logic.runtime.constants import EMOTION_DECAY_PER_TURN, MAX_VALUE, MIN_VALUE
from core.models.entities import CharacterEntity


class EmotionDecayEngine:
    def advance_turn(self, entity: CharacterEntity) -> None:
        for emotion_name, drift in EMOTION_DECAY_PER_TURN.items():
            value = getattr(entity.emotions, emotion_name)
            next_value = max(MIN_VALUE, min(MAX_VALUE, value - drift))
            setattr(entity.emotions, emotion_name, round(next_value, 4))
