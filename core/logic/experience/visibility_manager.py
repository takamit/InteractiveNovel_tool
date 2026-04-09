from __future__ import annotations


class VisibilityManager:
    def can_show_secret(self, *, mode: str, knowledge_state: str, visibility: str) -> bool:
        if mode == 'omniscient' or mode == 'analyst':
            return True
        if visibility == 'revealed':
            return True
        return knowledge_state in {'partially_known', 'known'}
