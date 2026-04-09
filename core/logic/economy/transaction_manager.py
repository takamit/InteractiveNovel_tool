from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TransactionRecord:
    actor_id: str
    amount: float
    reason: str
