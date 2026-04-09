from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RuntimeEvent:
    trigger_type: str
    trigger_id: str
    summary: str
    payload: dict[str, Any] = field(default_factory=dict)
