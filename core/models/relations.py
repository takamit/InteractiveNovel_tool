from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RelationDelta:
    like: float = 0.0
    trust: float = 0.0
    suspicion: float = 0.0
    attachment: float = 0.0
    resentment: float = 0.0
