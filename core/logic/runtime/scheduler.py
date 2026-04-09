from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(slots=True)
class ScheduledActor:
    entity_id: str
    initiative: float
    social_priority: float


class TurnScheduler:
    """Deterministic turn ordering helper used by high level runners."""

    def build_schedule(self, actors: Iterable[tuple[str, float, float]]) -> list[ScheduledActor]:
        schedule = [ScheduledActor(entity_id=entity_id, initiative=initiative, social_priority=social_priority) for entity_id, initiative, social_priority in actors]
        return sorted(schedule, key=lambda item: (item.initiative, item.social_priority, item.entity_id), reverse=True)
