from __future__ import annotations

from core.models.events import RuntimeEvent


class EventDispatcher:
    def dispatch(self, event: RuntimeEvent) -> dict[str, object]:
        return {
            'trigger_type': event.trigger_type,
            'trigger_id': event.trigger_id,
            'summary': event.summary,
            **event.payload,
        }
