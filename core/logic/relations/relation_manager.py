from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.logic.runtime.constants import MAX_VALUE, MIN_VALUE, RELATION_ACTION_EFFECTS, TARGET_REACTION_EFFECTS
from core.logic.runtime.world_state import WorldState
from core.models.entities import RelationRecord


@dataclass(slots=True)
class RelationUpdateResult:
    changed_pairs: list[tuple[str, str]]


class RelationManager:
    def _clamp(self, value: float) -> float:
        return round(max(MIN_VALUE, min(MAX_VALUE, value)), 4)

    def _apply_effect_bundle(self, relation: RelationRecord, effect: dict[str, float], scale: float = 1.0) -> None:
        if not effect:
            return
        mapping = {
            "like": (relation.basic, "like"),
            "trust": (relation.basic, "trust"),
            "respect": (relation.basic, "respect"),
            "fear": (relation.basic, "fear"),
            "suspicion": (relation.basic, "suspicion"),
            "interest": (relation.extended, "interest"),
            "dependence": (relation.extended, "dependence"),
            "attachment": (relation.extended, "attachment"),
            "attraction": (relation.extended, "attraction"),
            "intimacy": (relation.extended, "intimacy"),
            "desire": (relation.advanced, "desire"),
            "exclusivity": (relation.advanced, "exclusivity"),
            "obsession": (relation.advanced, "obsession"),
            "control": (relation.advanced, "control"),
            "devotion": (relation.advanced, "devotion"),
            "resentment": (relation.advanced, "resentment"),
            "maintenance": (relation, "maintenance"),
            "decay": (relation, "decay"),
        }
        for key, raw_delta in effect.items():
            target = mapping.get(key)
            if target is None:
                continue
            obj, attr = target
            setattr(obj, attr, self._clamp(getattr(obj, attr) + (raw_delta * scale)))

    def _refresh_labels(self, relation: RelationRecord) -> None:
        emotional = set(relation.labels.emotional)
        perception = set(relation.labels.perception)
        structural = set(relation.labels.structural)

        emotional.discard("warm")
        emotional.discard("cold")
        emotional.discard("volatile")
        emotional.discard("dependent")
        perception.discard("trusted")
        perception.discard("dangerous")
        perception.discard("unbalanced")

        trust_vector = relation.basic.trust + relation.extended.intimacy + relation.extended.attachment
        threat_vector = relation.basic.suspicion + relation.advanced.resentment + relation.basic.fear

        if trust_vector >= 140:
            emotional.add("warm")
            perception.add("trusted")
        if threat_vector >= 120:
            emotional.add("cold")
            perception.add("dangerous")
        if relation.extended.dependence + relation.advanced.obsession >= 95:
            emotional.add("dependent")
            perception.add("unbalanced")
        if relation.asymmetry >= 40:
            emotional.add("volatile")
            structural.add("asymmetry_axis")
        else:
            structural.discard("asymmetry_axis")

        relation.labels.emotional = sorted(emotional)
        relation.labels.perception = sorted(perception)
        relation.labels.structural = sorted(structural)

    def _recalculate_pair_metrics(self, relation: RelationRecord, reverse_relation: RelationRecord | None, memory: dict[str, Any]) -> None:
        relation.advanced.obsession = self._clamp(
            relation.advanced.obsession
            + (relation.extended.attachment * 0.008)
            + (relation.extended.dependence * 0.01)
            + (relation.advanced.exclusivity * 0.007)
            + (memory.get("long_term_charge", 0.0) * 0.03)
            - 0.18
        )
        relation.advanced.devotion = self._clamp(
            relation.advanced.devotion
            + (relation.basic.trust * 0.006)
            + (relation.extended.intimacy * 0.006)
            + max(0.0, memory.get("support_balance", 0.0)) * 0.08
            - 0.12
        )
        relation.advanced.resentment = self._clamp(
            relation.advanced.resentment
            + (relation.basic.suspicion * 0.006)
            + memory.get("breach_count", 0) * 0.35
            - (relation.basic.like * 0.0025)
            - 0.08
        )
        relation.extended.attachment = self._clamp(
            relation.extended.attachment
            + (relation.extended.intimacy * 0.005)
            + (relation.basic.like * 0.004)
            + memory.get("touch_streak", 0.0) * 0.04
            - 0.15
        )
        relation.extended.dependence = self._clamp(
            relation.extended.dependence
            + (relation.basic.trust * 0.003)
            + (relation.extended.intimacy * 0.0035)
            + max(0.0, memory.get("long_term_charge", 0.0)) * 0.02
            - 0.10
        )
        relation.decay = self._clamp(
            relation.decay
            + max(0.0, 38.0 - relation.maintenance) * 0.020
            + max(0.0, relation.basic.suspicion - relation.basic.trust) * 0.010
            + memory.get("breach_count", 0) * 0.12
        )

        if reverse_relation is not None:
            relation.asymmetry = self._clamp(
                abs(relation.basic.like - reverse_relation.basic.like) * 0.32
                + abs(relation.basic.trust - reverse_relation.basic.trust) * 0.32
                + abs(relation.extended.attachment - reverse_relation.extended.attachment) * 0.22
                + abs(relation.advanced.obsession - reverse_relation.advanced.obsession) * 0.14
            )
        else:
            relation.asymmetry = self._clamp(relation.asymmetry)

        trust_vector = relation.basic.trust + relation.extended.intimacy + relation.extended.attachment + relation.advanced.devotion * 0.6
        suspicion_vector = relation.basic.suspicion + relation.advanced.resentment + relation.basic.fear + relation.advanced.control * 0.4
        momentum = memory.get("support_balance", 0.0) + memory.get("touch_streak", 0.0) * 0.2 - memory.get("breach_count", 0) * 1.4
        if trust_vector - suspicion_vector >= 42.0 and momentum >= 0.0:
            relation.trend = "deepening"
        elif suspicion_vector - trust_vector >= 38.0:
            relation.trend = "deteriorating"
        elif relation.asymmetry >= 45.0:
            relation.trend = "asymmetric"
        elif abs(momentum) <= 2.0:
            relation.trend = "stagnant"
        elif momentum > 0:
            relation.trend = "warming"
        else:
            relation.trend = "volatile"
        self._refresh_labels(relation)

    def _apply_passive_decay(self, relation: RelationRecord, memory: dict[str, Any], current_turn: int) -> None:
        stale_turns = max(0, current_turn - int(memory.get("last_touched_turn", current_turn)))
        drift = relation.decay * (0.012 + stale_turns * 0.002)
        relation.basic.like = self._clamp(relation.basic.like - drift * 0.26)
        relation.basic.trust = self._clamp(relation.basic.trust - drift * 0.32)
        relation.extended.interest = self._clamp(relation.extended.interest - drift * 0.18)
        relation.extended.intimacy = self._clamp(relation.extended.intimacy - drift * 0.18)
        relation.extended.attachment = self._clamp(relation.extended.attachment - drift * 0.12)
        relation.maintenance = self._clamp(relation.maintenance - 0.35 - stale_turns * 0.03)
        memory["touch_streak"] = max(0.0, float(memory.get("touch_streak", 0.0)) - 0.35)
        memory["support_balance"] = float(memory.get("support_balance", 0.0)) * 0.96
        memory["long_term_charge"] = float(memory.get("long_term_charge", 0.0)) * 0.985

    def apply_action(self, state: WorldState, action: dict[str, Any]) -> RelationUpdateResult:
        actor_id = action["actor_id"]
        target_id = action.get("target_id")
        if not target_id:
            return RelationUpdateResult(changed_pairs=[])

        relation = state.get_relation(actor_id, target_id)
        reverse_relation = state.get_relation(target_id, actor_id)
        if relation is None:
            return RelationUpdateResult(changed_pairs=[])

        action_type = action["action_type"]
        actor = state.entities[actor_id]
        target = state.entities[target_id]
        actor_memory = state.get_relation_memory(actor_id, target_id)
        reverse_memory = state.get_relation_memory(target_id, actor_id)

        actor_scale = 1.0 + (actor.relation_tendency.trust_growth_rate - actor.relation_tendency.suspicion_growth_rate) / 300.0
        target_scale = 1.0 + (target.relation_tendency.trust_growth_rate - target.relation_tendency.suspicion_growth_rate) / 360.0
        if action_type == "confront":
            actor_scale = 1.0 + (actor.inner_profile.pride + actor.emotions.anger) / 220.0
            target_scale = 1.0 + (target.relation_tendency.suspicion_growth_rate + target.emotions.fear) / 260.0
            actor_memory["breach_count"] = int(actor_memory.get("breach_count", 0)) + 1
            reverse_memory["breach_count"] = int(reverse_memory.get("breach_count", 0)) + 1
            actor_memory["support_balance"] = float(actor_memory.get("support_balance", 0.0)) - 1.5
            reverse_memory["support_balance"] = float(reverse_memory.get("support_balance", 0.0)) - 1.0
        elif action_type in {"confide", "seek_help", "support"}:
            actor_scale = 1.0 + (actor.relation_tendency.attachment_speed + actor.emotions.affection) / 240.0
            target_scale = 1.0 + (target.relation_tendency.trust_growth_rate + target.inner_profile.maturity) / 280.0
            actor_memory["support_balance"] = float(actor_memory.get("support_balance", 0.0)) + 1.7
            reverse_memory["support_balance"] = float(reverse_memory.get("support_balance", 0.0)) + 1.1
        elif action_type in {"approach", "observe"}:
            actor_memory["support_balance"] = float(actor_memory.get("support_balance", 0.0)) + 0.4
        elif action_type == "withdraw":
            actor_memory["support_balance"] = float(actor_memory.get("support_balance", 0.0)) - 0.5
            reverse_memory["support_balance"] = float(reverse_memory.get("support_balance", 0.0)) - 0.3

        actor_memory["touch_streak"] = float(actor_memory.get("touch_streak", 0.0)) + 1.0
        reverse_memory["touch_streak"] = float(reverse_memory.get("touch_streak", 0.0)) + 0.4
        actor_memory["last_action"] = action_type
        reverse_memory["last_action"] = f"target_of_{action_type}"
        actor_memory["last_touched_turn"] = state.turn
        reverse_memory["last_touched_turn"] = state.turn
        actor_memory["long_term_charge"] = float(actor_memory.get("long_term_charge", 0.0)) + relation.basic.trust * 0.01 - relation.basic.suspicion * 0.01
        reverse_memory["long_term_charge"] = float(reverse_memory.get("long_term_charge", 0.0)) + (reverse_relation.basic.trust if reverse_relation else 0.0) * 0.008

        self._apply_effect_bundle(relation, RELATION_ACTION_EFFECTS.get(action_type, {}), scale=actor_scale)
        changed_pairs = [(actor_id, target_id)]
        if reverse_relation is not None:
            self._apply_effect_bundle(reverse_relation, TARGET_REACTION_EFFECTS.get(action_type, {}), scale=target_scale)
            changed_pairs.append((target_id, actor_id))

        self._recalculate_pair_metrics(relation, reverse_relation, actor_memory)
        if reverse_relation is not None:
            self._recalculate_pair_metrics(reverse_relation, relation, reverse_memory)

        return RelationUpdateResult(changed_pairs=changed_pairs)

    def apply_turn_decay(self, state: WorldState) -> None:
        for pair, relation in state.relations.items():
            memory = state.get_relation_memory(pair[0], pair[1])
            self._apply_passive_decay(relation, memory, state.turn)
            reverse_relation = state.relations.get((pair[1], pair[0]))
            self._recalculate_pair_metrics(relation, reverse_relation, memory)


RelationDynamics = RelationManager
