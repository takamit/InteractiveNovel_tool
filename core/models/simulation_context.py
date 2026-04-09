from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SimulationContext:
    world_name: str
    current_turn: int = 0
    seed: int = 42
    metadata: dict[str, Any] = field(default_factory=dict)
