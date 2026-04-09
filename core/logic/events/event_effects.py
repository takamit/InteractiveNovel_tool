from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.logic.runtime.constants import MAX_VALUE, MIN_VALUE
from core.logic.runtime.world_state import WorldState
from core.models.entities import RelationRecord


@dataclass(slots=True)
class SecondaryReactionEvent:
    trigger_type: str
    trigger_id: str
    summary: str
    affected_entities: list[str]


class SecondaryReactionEngine:
    def _clamp(self, value: float) -> float:
        return round(max(MIN_VALUE, min(MAX_VALUE, value)), 4)

    def _relation(self, state: WorldState, source_id: str, target_id: str) -> RelationRecord | None:
        return state.get_relation(source_id, target_id)

    def _bump_relation(self, relation: RelationRecord | None, path: str, delta: float) -> None:
        if relation is None:
            return
        obj_name, attr = path.split('.', 1)
        obj = getattr(relation, obj_name)
        setattr(obj, attr, self._clamp(getattr(obj, attr) + delta))

    def _bump_status(self, state: WorldState, entity_id: str, field_name: str, delta: float) -> None:
        entity = state.entities.get(entity_id)
        if entity is None:
            return
        setattr(entity.status, field_name, self._clamp(getattr(entity.status, field_name) + delta))

    def _bump_emotion(self, state: WorldState, entity_id: str, field_name: str, delta: float) -> None:
        entity = state.entities.get(entity_id)
        if entity is None:
            return
        setattr(entity.emotions, field_name, self._clamp(getattr(entity.emotions, field_name) + delta))

    def _apply_secret_reaction(self, state: WorldState, secret_event: dict[str, Any]) -> list[SecondaryReactionEvent]:
        secret_id = secret_event['secret_id']
        visibility = secret_event['new_visibility']
        events: list[SecondaryReactionEvent] = []

        if secret_id == 'secret_001':
            self._bump_status(state, 'char_002', 'stress', -4.0 if visibility == 'revealed' else -1.5)
            self._bump_emotion(state, 'char_001', 'affection', 2.5)
            self._bump_relation(self._relation(state, 'char_002', 'char_001'), 'basic.trust', 6.0)
            self._bump_relation(self._relation(state, 'char_002', 'char_001'), 'extended.intimacy', 5.0)
            events.append(SecondaryReactionEvent('secret', secret_id, '白峰澪が神代湊への警戒を少し下げた。', ['char_001', 'char_002']))
        elif secret_id == 'secret_002':
            self._bump_status(state, 'char_001', 'stress', 3.2)
            self._bump_status(state, 'char_003', 'stress', 2.6)
            self._bump_relation(self._relation(state, 'char_001', 'char_003'), 'basic.suspicion', 6.5)
            self._bump_relation(self._relation(state, 'char_003', 'char_001'), 'advanced.control', 4.2)
            events.append(SecondaryReactionEvent('secret', secret_id, '神代湊と九条迅の対立が一段深く固定された。', ['char_001', 'char_003']))
        elif secret_id == 'secret_003':
            self._bump_status(state, 'char_008', 'stress', 5.1)
            self._bump_relation(self._relation(state, 'char_008', 'char_005'), 'basic.suspicion', 9.0)
            self._bump_relation(self._relation(state, 'char_008', 'char_005'), 'basic.trust', -7.0)
            self._bump_relation(self._relation(state, 'char_005', 'char_008'), 'advanced.control', 3.5)
            events.append(SecondaryReactionEvent('secret', secret_id, '相沢蓮が黒瀬環への不信を強め、情報流通がぎくしゃくし始めた。', ['char_005', 'char_008']))
        elif secret_id == 'secret_004':
            delta = 10.0 if visibility == 'revealed' else 4.0
            self._bump_status(state, 'char_001', 'stress', 4.0)
            self._bump_relation(self._relation(state, 'char_007', 'char_001'), 'extended.dependence', delta)
            self._bump_relation(self._relation(state, 'char_007', 'char_001'), 'advanced.obsession', delta * 0.7)
            self._bump_relation(self._relation(state, 'char_001', 'char_007'), 'basic.suspicion', 3.2)
            events.append(SecondaryReactionEvent('secret', secret_id, '東雲紗良の依存が反応を呼び、神代湊の負荷が増した。', ['char_001', 'char_007']))
        elif secret_id == 'secret_005':
            self._bump_status(state, 'char_006', 'stress', -3.4)
            self._bump_relation(self._relation(state, 'char_001', 'char_006'), 'basic.trust', 4.3)
            self._bump_relation(self._relation(state, 'char_004', 'char_006'), 'basic.trust', 5.2)
            events.append(SecondaryReactionEvent('secret', secret_id, '篠崎朱音の仮面が少し剥がれ、理解の糸口ができた。', ['char_001', 'char_004', 'char_006']))

        pressure = state.secret_pressure.get(secret_id, 0.0)
        if pressure >= 20.0:
            for entity_id in secret_event.get('affected_entities', []):
                self._bump_status(state, entity_id, 'rumor_level', 1.5)
            events.append(SecondaryReactionEvent('secret_tail', secret_id, '露見した秘密の熱が残り、噂がじわじわ広がっている。', list(secret_event.get('affected_entities', []))))
        return events

    def _apply_action_reaction(self, state: WorldState, action: dict[str, Any]) -> list[SecondaryReactionEvent]:
        actor_id = action['actor_id']
        target_id = action.get('target_id')
        action_type = action['action_type']
        if not target_id:
            return []

        events: list[SecondaryReactionEvent] = []
        if action_type == 'confront':
            self._bump_status(state, actor_id, 'stress', 1.8)
            self._bump_status(state, target_id, 'stress', 2.2)
            self._bump_relation(self._relation(state, target_id, actor_id), 'advanced.resentment', 2.8)
            events.append(SecondaryReactionEvent('action', f'{actor_id}:{action_type}', '対立の余波で相手側の反感が残った。', [actor_id, target_id]))
        elif action_type == 'support':
            self._bump_status(state, target_id, 'stress', -2.0)
            self._bump_relation(self._relation(state, target_id, actor_id), 'basic.trust', 1.8)
            events.append(SecondaryReactionEvent('action', f'{actor_id}:{action_type}', '支援行動が静かな信頼の返礼を生んだ。', [actor_id, target_id]))
        elif action_type == 'withdraw':
            self._bump_relation(self._relation(state, target_id, actor_id), 'basic.suspicion', 1.2)
            events.append(SecondaryReactionEvent('action', f'{actor_id}:{action_type}', '距離を取ったことで、相手側に小さな違和感が残った。', [actor_id, target_id]))
        elif action_type == 'confide':
            self._bump_emotion(state, target_id, 'affection', 1.4)
            self._bump_relation(self._relation(state, target_id, actor_id), 'extended.intimacy', 1.3)
            events.append(SecondaryReactionEvent('action', f'{actor_id}:{action_type}', '打ち明け話が相互理解の余韻を残した。', [actor_id, target_id]))
        return events

    def _apply_world_pressure_fallout(self, state: WorldState) -> list[SecondaryReactionEvent]:
        emitted: list[SecondaryReactionEvent] = []
        for secret_id, pressure in list(state.secret_pressure.items()):
            if pressure <= 0:
                continue
            if pressure >= 35.0:
                for entity in state.entities.values():
                    entity.status.rumor_level = self._clamp(entity.status.rumor_level + 0.5)
                emitted.append(SecondaryReactionEvent('world', secret_id, '秘密の余熱が世界全体の空気を少し刺々しくしている。', list(state.entities.keys())))
            state.secret_pressure[secret_id] = self._clamp(max(0.0, pressure - 2.6))
        return emitted

    def process_turn(
        self,
        state: WorldState,
        actions: list[dict[str, Any]],
        secret_events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        emitted: list[SecondaryReactionEvent] = []
        for secret_event in secret_events:
            emitted.extend(self._apply_secret_reaction(state, secret_event))
        for action in actions:
            emitted.extend(self._apply_action_reaction(state, action))
        emitted.extend(self._apply_world_pressure_fallout(state))

        payloads = [
            {
                'trigger_type': event.trigger_type,
                'trigger_id': event.trigger_id,
                'summary': event.summary,
                'affected_entities': event.affected_entities,
            }
            for event in emitted
        ]
        state.secondary_events.extend(payloads)
        for payload in payloads:
            state.log_event('secondary_reaction', payload)
        return payloads
