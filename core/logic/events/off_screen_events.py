from __future__ import annotations

from core.logic.runtime.constants import MAX_VALUE, MIN_VALUE
from core.logic.runtime.world_state import WorldState


class OffscreenEventEngine:
    def _clamp(self, value: float) -> float:
        return round(max(MIN_VALUE, min(MAX_VALUE, value)), 4)

    def process_turn(self, state: WorldState) -> list[dict[str, object]]:
        emitted: list[dict[str, object]] = []
        hottest = sorted(state.location_heat.items(), key=lambda item: item[1], reverse=True)
        if hottest:
            location_id, heat = hottest[0]
            if heat >= 18.0:
                occupants = [entity.id for entity in state.entities.values() if entity.status.current_location_id == location_id]
                for entity_id in occupants:
                    entity = state.entities[entity_id]
                    entity.status.rumor_level = self._clamp(entity.status.rumor_level + heat * 0.015)
                    entity.status.stress = self._clamp(entity.status.stress + heat * 0.010)
                emitted.append(
                    {
                        'trigger_type': 'offscreen_rumor_echo',
                        'trigger_id': location_id,
                        'summary': f'{location_id} 周辺で出来事の余波が続き、見えないところで噂が補強された。',
                        'affected_entities': occupants,
                    }
                )

        strongest_secret = sorted(state.secret_pressure.items(), key=lambda item: item[1], reverse=True)
        if strongest_secret:
            secret_id, pressure = strongest_secret[0]
            if pressure >= 14.0:
                for entity in state.entities.values():
                    secret_state = state.secrets[secret_id].knowledge_states.get(entity.id, 'unknown')
                    if secret_state in {'rumored', 'partially_known'}:
                        entity.status.rumor_level = self._clamp(entity.status.rumor_level + pressure * 0.010)
                emitted.append(
                    {
                        'trigger_type': 'offscreen_secret_drift',
                        'trigger_id': secret_id,
                        'summary': f'{secret_id} の話題が視界外でもじわじわ広がっている。',
                        'affected_entities': [entity.id for entity in state.entities.values() if state.secrets[secret_id].knowledge_states.get(entity.id) in {'rumored', 'partially_known'}],
                    }
                )

        if state.institution_pressure >= 10.0:
            affected = []
            for entity in state.entities.values():
                if entity.status.social_position in {'middle', 'middle_low', 'unstable_middle', 'lower'}:
                    entity.status.stress = self._clamp(entity.status.stress + state.institution_pressure * 0.012)
                    affected.append(entity.id)
            emitted.append(
                {
                    'trigger_type': 'offscreen_institution_notice',
                    'trigger_id': 'institution',
                    'summary': '制度側の視線が強まり、下位層ほど息苦しさを覚え始めている。',
                    'affected_entities': affected,
                }
            )
            state.institution_pressure = self._clamp(max(0.0, state.institution_pressure - 2.2))

        state.offscreen_events = list(emitted)
        for payload in emitted:
            state.log_event('offscreen_event', payload)
        return emitted


OffScreenEventEngine = OffscreenEventEngine
