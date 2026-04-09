from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ActionCandidate:
    action_type: str
    actor_id: str
    target_id: str | None = None
    location_id: str | None = None
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
