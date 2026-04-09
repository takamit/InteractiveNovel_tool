from __future__ import annotations

from core.models.entities import CharacterEntity


class EmotionBiasEngine:
    def action_bias(self, entity: CharacterEntity, action_type: str) -> float:
        if action_type in {'approach', 'support', 'confide'}:
            return round(entity.emotions.affection * 0.08 - entity.emotions.fear * 0.03, 4)
        if action_type == 'confront':
            return round(entity.emotions.anger * 0.12 - entity.emotions.affection * 0.02, 4)
        if action_type in {'withdraw', 'wait'}:
            return round(entity.emotions.fear * 0.08 + entity.emotions.sadness * 0.04, 4)
        return round(entity.emotions.joy * 0.03, 4)
