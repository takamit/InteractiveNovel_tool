from __future__ import annotations

from dataclasses import dataclass

from core.logic.runtime.constants import SECRET_KNOWLEDGE_ORDER, SECRET_VISIBILITY_ORDER
from core.logic.runtime.world_state import WorldState


@dataclass(slots=True)
class SecretExposureEvent:
    secret_id: str
    old_visibility: str
    new_visibility: str
    reason: str
    affected_entities: list[str]


class SecretExposureEngine:
    def _advance_visibility(self, current: str, target: str) -> str:
        current_idx = SECRET_VISIBILITY_ORDER.index(current)
        target_idx = SECRET_VISIBILITY_ORDER.index(target)
        return SECRET_VISIBILITY_ORDER[max(current_idx, target_idx)]

    def _advance_knowledge(self, current: str, target: str) -> str:
        current_idx = SECRET_KNOWLEDGE_ORDER.index(current)
        target_idx = SECRET_KNOWLEDGE_ORDER.index(target)
        return SECRET_KNOWLEDGE_ORDER[max(current_idx, target_idx)]

    def _visibility_target(self, state: WorldState, secret_id: str, action: dict[str, object]) -> tuple[str | None, str | None, list[str]]:
        actor_id = str(action["actor_id"])
        target_id = action.get("target_id")
        target_id = str(target_id) if target_id else None
        actor = state.entities[actor_id]
        location = state.locations.get(actor.status.current_location_id)
        relation = state.get_relation(actor_id, target_id) if target_id else None
        location_id = actor.status.current_location_id
        action_type = str(action["action_type"])
        affected = [entity_id for entity_id in [actor_id, target_id] if entity_id]

        if secret_id == "secret_001":
            if action_type == "confide" and {actor_id, target_id} == {"char_001", "char_002"} and relation and relation.basic.trust >= 25.0:
                return "revealed", "private_confession_axis", affected
            if action_type in {"observe", "confront"} and location and location.rumor_spread_rate >= 60.0:
                return "rumored", "rumor_chain_investigation", ["char_004", "char_008"]
        elif secret_id == "secret_002":
            if action_type == "confront" and {actor_id, target_id} == {"char_001", "char_003"}:
                return "revealed", "direct_confrontation_scene", affected
            if action_type == "observe" and actor_id == "char_004" and target_id == "char_003":
                return "implied", "third_party_observation", ["char_004"]
        elif secret_id == "secret_003":
            if action_type == "observe" and actor_id == "char_004" and target_id in {"char_005", "char_008"}:
                return "implied", "cross_check_multiple_rumors", ["char_004"]
            if action_type == "confront" and {actor_id, target_id} == {"char_005", "char_008"}:
                return "revealed", "channel_breakdown", affected
        elif secret_id == "secret_004":
            if action_type in {"confide", "seek_help"} and actor_id == "char_007" and target_id == "char_001":
                return "revealed", "dependency_confession", affected
            if location_id == "loc_infirmary_corridor" and actor_id == "char_007" and action_type in {"withdraw", "seek_help"}:
                return "implied", "infirmary_scene", ["char_001", "char_004", "char_007"]
        elif secret_id == "secret_005":
            if action_type == "confide" and actor_id == "char_006" and target_id in {"char_001", "char_004"}:
                return "revealed", "private_confession_scene", affected
            if action_type == "withdraw" and actor_id == "char_006" and location and location.social_pressure >= 40.0:
                return "implied", "pressure_from_social_group", ["char_004", "char_005"]

        return None, None, []

    def _apply_long_tail(self, state: WorldState, secret_id: str, visibility: str, affected: list[str]) -> None:
        base_pressure = {"implied": 6.0, "rumored": 12.0, "revealed": 18.0}.get(visibility, 0.0)
        current = state.secret_pressure.get(secret_id, 0.0)
        state.secret_pressure[secret_id] = round(min(100.0, current + base_pressure), 4)
        for entity_id in affected:
            entity = state.entities.get(entity_id)
            if entity is None:
                continue
            entity.status.rumor_level = min(100.0, round(entity.status.rumor_level + base_pressure * 0.18, 4))
            entity.status.hidden_reputation = max(0.0, round(entity.status.hidden_reputation - base_pressure * 0.08, 4))

    def evaluate_action(self, state: WorldState, action: dict[str, object]) -> list[SecretExposureEvent]:
        exposure_events: list[SecretExposureEvent] = []
        for secret in state.secrets.values():
            target_visibility, reason, affected = self._visibility_target(state, secret.id, action)
            if not target_visibility or not reason:
                continue
            previous_visibility = secret.visibility
            secret.visibility = self._advance_visibility(secret.visibility, target_visibility)
            if secret.visibility == previous_visibility:
                continue

            for entity_id in affected:
                if entity_id in secret.knowledge_states:
                    secret.knowledge_states[entity_id] = self._advance_knowledge(
                        secret.knowledge_states[entity_id],
                        "known" if secret.visibility == "revealed" else "partially_known",
                    )
            if secret.visibility in {"rumored", "revealed"}:
                for entity_id, current in list(secret.knowledge_states.items()):
                    if entity_id not in affected and current == "unknown":
                        secret.knowledge_states[entity_id] = "rumored"
            if secret.visibility == "revealed":
                for entity_id, current in list(secret.knowledge_states.items()):
                    if current == "rumored":
                        secret.knowledge_states[entity_id] = "partially_known"

            self._apply_long_tail(state, secret.id, secret.visibility, affected)
            exposure_events.append(
                SecretExposureEvent(
                    secret_id=secret.id,
                    old_visibility=previous_visibility,
                    new_visibility=secret.visibility,
                    reason=reason,
                    affected_entities=affected,
                )
            )
        return exposure_events
