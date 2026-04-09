from __future__ import annotations

from typing import Any

from core.logic.runtime.constants import MAX_VALUE, MIN_VALUE, SOCIAL_POSITION_POWER
from core.logic.runtime.world_state import WorldState


class HierarchyManager:
    def _clamp(self, value: float) -> float:
        return round(max(MIN_VALUE, min(MAX_VALUE, value)), 4)

    def _power(self, social_position: str) -> float:
        return SOCIAL_POSITION_POWER.get(social_position, 50.0)

    def apply_hierarchy_response(self, state: WorldState, action: dict[str, Any]) -> list[dict[str, Any]]:
        actor = state.entities[action['actor_id']]
        target = state.entities.get(action.get('target_id')) if action.get('target_id') else None
        location = state.locations.get(action.get('location_id') or actor.status.current_location_id)
        if target is None or location is None:
            return []

        actor_power = self._power(actor.status.social_position)
        target_power = self._power(target.status.social_position)
        gap = target_power - actor_power
        if action['action_type'] not in {'confront', 'seek_help', 'confide'}:
            return []

        institutional_bias = 1.35 if location.category in {'institution', 'classroom'} else 0.75
        visibility_bias = 1.15 if location.visibility in {'public', 'semi_public'} else 0.65
        sanction_pressure = max(0.0, gap) * 0.22 * institutional_bias * visibility_bias
        protection_pressure = max(0.0, -gap) * 0.11 * visibility_bias
        emitted: list[dict[str, Any]] = []

        if sanction_pressure >= 3.0:
            actor.status.visible_reputation = self._clamp(actor.status.visible_reputation - sanction_pressure * 0.22)
            actor.status.stress = self._clamp(actor.status.stress + sanction_pressure * 0.18)
            target.status.visible_reputation = self._clamp(target.status.visible_reputation + sanction_pressure * 0.10)
            state.institution_pressure = self._clamp(state.institution_pressure + sanction_pressure * 0.24)
            emitted.append(
                {
                    'trigger_type': 'hierarchy_sanction',
                    'trigger_id': f"{actor.id}->{target.id}",
                    'summary': f'{actor.name.full_name} の行動は階層差に阻まれ、表向きの立場を少し失った。',
                    'affected_entities': [actor.id, target.id],
                    'pressure_score': round(sanction_pressure, 4),
                }
            )
        elif protection_pressure >= 2.0 and action['action_type'] in {'seek_help', 'confide'}:
            actor.status.visible_reputation = self._clamp(actor.status.visible_reputation + protection_pressure * 0.08)
            target.status.visible_reputation = self._clamp(target.status.visible_reputation + protection_pressure * 0.05)
            emitted.append(
                {
                    'trigger_type': 'hierarchy_cover',
                    'trigger_id': f"{actor.id}->{target.id}",
                    'summary': f'{target.name.full_name} の立場差が、{actor.name.full_name} の行動を目立ちにくくした。',
                    'affected_entities': [actor.id, target.id],
                    'pressure_score': round(protection_pressure, 4),
                }
            )
        return emitted
