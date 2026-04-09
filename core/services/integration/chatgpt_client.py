from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ChatClientConfig:
    enabled: bool = False
    model_name: str = 'disabled'


class ChatGPTClient:
    def __init__(self, config: ChatClientConfig | None = None) -> None:
        self.config = config or ChatClientConfig()

    def is_enabled(self) -> bool:
        return self.config.enabled
