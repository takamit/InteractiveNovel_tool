from __future__ import annotations

from typing import Any

from core.logic.runtime.world_state import WorldState
from ui.components.play.dialogue_renderer import EmotionDialogueRenderer


class NarrativeRenderer:
    def __init__(self) -> None:
        self.dialogue_renderer = EmotionDialogueRenderer()

    def render_action(self, state: WorldState, action: dict[str, Any], *, mode: str, focal_id: str | None) -> list[str]:
        lines = [self.dialogue_renderer.render_actor_line(state, action, focal_id=focal_id, mode=mode)]
        spoken = self.dialogue_renderer.render_spoken_line(state, action)
        if spoken:
            lines.append(spoken)
        reaction = self.dialogue_renderer.render_reaction_line(state, action, focal_id=focal_id)
        if reaction:
            lines.append(reaction)
        return [line for line in lines if line]
