from __future__ import annotations

from ui.components.meta_filter import remove_meta_lines
from ui.components.modes import OutputMode


class OutputRouter:
    def __init__(self, mode: OutputMode) -> None:
        self.mode = mode

    def route(self, text: str) -> str:
        if self.mode == OutputMode.PLAY:
            return remove_meta_lines(text)
        return text
