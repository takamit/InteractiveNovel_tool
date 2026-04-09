from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ItemRecord:
    item_id: str
    label: str
    rarity: str = 'common'
