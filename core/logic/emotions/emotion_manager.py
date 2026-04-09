from __future__ import annotations

from core.models.entities import CharacterEntity
from core.logic.emotions.emotion_decay import EmotionDecayEngine
from core.logic.emotions.breakdown_engine import EmotionalBreakdownEngine


class EmotionStateManager:
    def __init__(self) -> None:
        self.decay_engine = EmotionDecayEngine()
        self.breakdown_engine = EmotionalBreakdownEngine()

    def advance_turn(self, entity: CharacterEntity) -> dict[str, str | None]:
        self.decay_engine.advance_turn(entity)
        return {'breakdown_risk': self.breakdown_engine.check(entity)}
