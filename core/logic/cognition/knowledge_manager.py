from __future__ import annotations

from core.logic.runtime.constants import SECRET_KNOWLEDGE_ORDER
from core.models.entities import SecretRecord


class KnowledgeStateManager:
    def promote(self, secret: SecretRecord, entity_id: str, target_state: str) -> None:
        current = secret.knowledge_states.get(entity_id, 'unknown')
        if SECRET_KNOWLEDGE_ORDER.index(target_state) > SECRET_KNOWLEDGE_ORDER.index(current):
            secret.knowledge_states[entity_id] = target_state
