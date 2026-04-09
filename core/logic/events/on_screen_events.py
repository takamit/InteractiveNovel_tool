from __future__ import annotations

from core.models.events import RuntimeEvent


class OnScreenEventComposer:
    def compose(self, summary: str, *, trigger_id: str = 'screen') -> RuntimeEvent:
        return RuntimeEvent(trigger_type='on_screen', trigger_id=trigger_id, summary=summary)
