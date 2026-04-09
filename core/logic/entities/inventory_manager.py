from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InventoryState:
    items: dict[str, int] = field(default_factory=dict)


class InventoryManager:
    def add(self, inventory: InventoryState, item_id: str, amount: int = 1) -> None:
        inventory.items[item_id] = inventory.items.get(item_id, 0) + max(0, amount)

    def remove(self, inventory: InventoryState, item_id: str, amount: int = 1) -> None:
        current = inventory.items.get(item_id, 0)
        updated = max(0, current - max(0, amount))
        if updated == 0:
            inventory.items.pop(item_id, None)
        else:
            inventory.items[item_id] = updated
