from __future__ import annotations

from typing import Any

from core.logic.runtime.world_state import WorldState
from ui.components.play.dialogue_renderer import EmotionDialogueRenderer


class PlayerChoicePresenter:
    def __init__(self) -> None:
        self.dialogue_renderer = EmotionDialogueRenderer()

    def present_options(self, state: WorldState, actor_id: str, options: list[dict[str, Any]]) -> list[dict[str, Any]]:
        presented = []
        for index, option in enumerate(options, start=1):
            item = dict(option)
            item["index"] = index
            item["choice_label"] = self.dialogue_renderer.choice_prompt(state, actor_id, option)
            item["choice_detail"] = self.dialogue_renderer.choice_detail(state, actor_id, option)
            item["action_label"] = self.dialogue_renderer.action_label(str(option["action_type"]))
            presented.append(item)
        return presented
