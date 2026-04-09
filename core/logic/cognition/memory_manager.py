from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EpisodicMemory:
    entity_id: str
    entries: list[str] = field(default_factory=list)


class MemoryManager:
    def remember(self, memory: EpisodicMemory, note: str) -> None:
        memory.entries.append(note)
        if len(memory.entries) > 50:
            del memory.entries[:-50]
