from __future__ import annotations

from core.models.events import RuntimeEvent


class EventRegistry:
    def __init__(self) -> None:
        self._events: list[RuntimeEvent] = []

    def push(self, event: RuntimeEvent) -> None:
        self._events.append(event)

    def drain(self) -> list[RuntimeEvent]:
        events = list(self._events)
        self._events.clear()
        return events
