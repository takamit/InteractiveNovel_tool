from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.logic.runtime.constants import MAX_VALUE, MIN_VALUE
from core.logic.runtime.world_state import WorldState


@dataclass(slots=True)
class FactionPressureResult:
    faction_id: str
    pressure_score: float
    member_ids: list[str]
    summary: str


class FactionManager:
    def _clamp(self, value: float) -> float:
        return round(max(MIN_VALUE, min(MAX_VALUE, value)), 4)

    def infer_faction_id(self, entity: Any) -> str:
        if entity.status.current_location_id == 'loc_student_council' or entity.role.secondary == 'student_council_aide':
            return 'institutional_core'
        if entity.status.social_position in {'upper', 'upper_middle'}:
            return 'social_core'
        if entity.status.current_location_id == 'loc_library_hall' or entity.role.primary == 'observer':
            return 'quiet_observers'
        if entity.status.social_position == 'lower' or entity.role.primary in {'unstable_actor', 'outsider'}:
            return 'peripheral'
        return 'general_students'

    def build_membership(self, state: WorldState) -> dict[str, list[str]]:
        factions: dict[str, list[str]] = {}
        for entity in state.entities.values():
            faction_id = self.infer_faction_id(entity)
            factions.setdefault(faction_id, []).append(entity.id)
        return factions

    def apply_group_pressure(self, state: WorldState, action: dict[str, Any]) -> list[dict[str, Any]]:
        actor = state.entities[action['actor_id']]
        target = state.entities.get(action.get('target_id')) if action.get('target_id') else None
        faction_id = self.infer_faction_id(actor)
        member_ids = self.build_membership(state).get(faction_id, [])
        location = state.locations.get(action.get('location_id') or actor.status.current_location_id)
        public_factor = 1.15 if location and location.visibility in {'public', 'semi_public'} else 0.55
        action_weight = {
            'confront': 1.4,
            'confide': 0.9,
            'seek_help': 0.75,
            'support': 0.65,
            'withdraw': 0.45,
            'observe': 0.35,
            'approach': 0.5,
            'wait': 0.15,
        }.get(action['action_type'], 0.4)
        pressure_score = self._clamp((state.world_tension * 0.25 + (location.social_pressure if location else 0.0) * 0.30) * public_factor * action_weight)
        if pressure_score <= 8.0:
            return []

        state.faction_climate[faction_id] = self._clamp(state.faction_climate.get(faction_id, 0.0) + pressure_score * 0.22)
        emitted: list[dict[str, Any]] = []
        for member_id in member_ids:
            if member_id == actor.id:
                continue
            member = state.entities[member_id]
            member.status.stress = self._clamp(member.status.stress + pressure_score * 0.015)
            member.status.rumor_level = self._clamp(member.status.rumor_level + pressure_score * 0.011)
            if target is not None and action['action_type'] == 'confront':
                relation = state.get_relation(member_id, target.id)
                if relation is not None:
                    relation.basic.suspicion = self._clamp(relation.basic.suspicion + pressure_score * 0.025)
            if action['action_type'] == 'confide' and target is not None:
                relation = state.get_relation(member_id, actor.id)
                if relation is not None:
                    relation.extended.interest = self._clamp(relation.extended.interest + pressure_score * 0.018)

        emitted.append(
            {
                'trigger_type': 'faction_pressure',
                'trigger_id': faction_id,
                'pressure_score': pressure_score,
                'summary': f'{faction_id} の空気が動き、周辺メンバーが出来事に反応し始めた。',
                'affected_entities': [member_id for member_id in member_ids if member_id != actor.id],
            }
        )
        return emitted
