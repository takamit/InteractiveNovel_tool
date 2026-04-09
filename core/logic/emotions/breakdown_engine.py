from __future__ import annotations

from core.models.entities import CharacterEntity


class EmotionalBreakdownEngine:
    def check(self, entity: CharacterEntity) -> str | None:
        if entity.status.stress >= 88 and entity.emotions.fear >= 55:
            return 'panic_spike'
        if entity.status.stress >= 82 and entity.emotions.sadness >= 55:
            return 'shutdown_risk'
        if entity.status.stress >= 78 and entity.emotions.anger >= 60:
            return 'lashing_out_risk'
        return None
