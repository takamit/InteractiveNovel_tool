from __future__ import annotations

from typing import Any

from core.logic.runtime.constants import MAX_VALUE, MIN_VALUE
from core.logic.runtime.world_state import WorldState


class ReputationManager:
    def _clamp(self, value: float) -> float:
        return round(max(MIN_VALUE, min(MAX_VALUE, value)), 4)

    def apply_public_reputation_shift(self, state: WorldState, action: dict[str, Any]) -> list[dict[str, Any]]:
        actor = state.entities[action['actor_id']]
        target = state.entities.get(action.get('target_id')) if action.get('target_id') else None
        location = state.locations.get(action.get('location_id') or actor.status.current_location_id)
        if location is None:
            return []

        publicity = (100.0 - location.privacy_level) * 0.45 + location.rumor_spread_rate * 0.35 + state.world_tension * 0.20
        publicity = self._clamp(publicity)
        if publicity <= 12.0:
            return []

        effect_map = {
            'support': (0.24, -0.08),
            'seek_help': (0.10, 0.05),
            'confide': (0.08, 0.14),
            'confront': (-0.22, 0.20),
            'withdraw': (-0.10, 0.08),
            'approach': (0.06, 0.03),
            'observe': (0.02, 0.04),
            'wait': (0.00, 0.00),
        }
        rep_scale, rumor_scale = effect_map.get(action['action_type'], (0.0, 0.0))
        visible_delta = publicity * rep_scale * 0.10
        rumor_delta = publicity * rumor_scale * 0.10
        actor.status.visible_reputation = self._clamp(actor.status.visible_reputation + visible_delta)
        actor.status.rumor_level = self._clamp(actor.status.rumor_level + rumor_delta)
        if target is not None and action['action_type'] == 'support':
            target.status.visible_reputation = self._clamp(target.status.visible_reputation + publicity * 0.04)
        if target is not None and action['action_type'] == 'confront':
            target.status.rumor_level = self._clamp(target.status.rumor_level + publicity * 0.06)

        state.reputation_pressure_log.append(
            {
                'turn': state.turn,
                'actor_id': actor.id,
                'target_id': target.id if target else None,
                'action_type': action['action_type'],
                'publicity': publicity,
                'visible_delta': round(visible_delta, 4),
                'rumor_delta': round(rumor_delta, 4),
            }
        )
        return [
            {
                'trigger_type': 'reputation_shift',
                'trigger_id': actor.id,
                'summary': f'{actor.name.full_name} の行動が周囲の評価に薄く残った。',
                'affected_entities': [entity_id for entity_id in [actor.id, target.id if target else None] if entity_id],
                'pressure_score': publicity,
            }
        ]
