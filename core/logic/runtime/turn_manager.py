from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from core.logic.runtime.constants import (
    ACTION_ENGINE_AFFINITY,
    ACTION_IDEOLOGY_BIAS,
    DEFAULT_NEED_DRIFT,
    EMOTION_DECAY_PER_TURN,
    MAX_VALUE,
    MIN_VALUE,
    NEED_PRIORITY_WEIGHTS,
    SOCIAL_POSITION_POWER,
)
from core.logic.runtime.world_state import WorldState
from core.logic.environment.location_manager import WorldPressureEngine
from core.logic.events.event_effects import SecondaryReactionEngine
from core.logic.events.off_screen_events import OffscreenEventEngine
from core.logic.relations.relation_manager import RelationManager
from core.logic.secrets.exposure_engine import SecretExposureEngine
from core.logic.society.faction_manager import FactionManager
from core.logic.society.hierarchy_manager import HierarchyManager
from core.logic.society.reputation_manager import ReputationManager


@dataclass(slots=True)
class PlayerTurnChoice:
    actor_id: str
    action_type: str
    target_id: str | None = None


@dataclass(slots=True)
class TurnResult:
    turn: int
    actions: list[dict[str, Any]]
    highlights: list[str]
    secret_events: list[dict[str, Any]]
    secondary_events: list[dict[str, Any]]


class TurnManager:
    def __init__(self) -> None:
        self.relation_manager = RelationManager()
        self.secret_exposure_engine = SecretExposureEngine()
        self.secondary_reaction_engine = SecondaryReactionEngine()
        self.world_pressure_engine = WorldPressureEngine()
        self.reputation_manager = ReputationManager()
        self.hierarchy_manager = HierarchyManager()
        self.faction_manager = FactionManager()
        self.offscreen_event_engine = OffscreenEventEngine()

    def _clamp(self, value: float) -> float:
        return round(max(MIN_VALUE, min(MAX_VALUE, value)), 4)

    def _update_needs(self, state: WorldState) -> None:
        for entity in state.entities.values():
            entity.needs.survival.hunger = self._clamp(entity.needs.survival.hunger + DEFAULT_NEED_DRIFT['hunger'])
            entity.needs.survival.thirst = self._clamp(entity.needs.survival.thirst + DEFAULT_NEED_DRIFT['thirst'])
            entity.needs.survival.sleepiness = self._clamp(entity.needs.survival.sleepiness + DEFAULT_NEED_DRIFT['sleepiness'])
            entity.needs.survival.health = self._clamp(
                entity.needs.survival.health + DEFAULT_NEED_DRIFT['health'] - (entity.status.stress / 200.0) - (entity.status.injury / 250.0)
            )
            entity.needs.reproduction.sexual_desire = self._clamp(entity.needs.reproduction.sexual_desire + DEFAULT_NEED_DRIFT['sexual_desire'])
            entity.needs.reproduction.intimacy = self._clamp(entity.needs.reproduction.intimacy + DEFAULT_NEED_DRIFT['intimacy'])
            entity.needs.psychological.belonging = self._clamp(entity.needs.psychological.belonging + DEFAULT_NEED_DRIFT['belonging'])
            entity.needs.psychological.approval = self._clamp(entity.needs.psychological.approval + DEFAULT_NEED_DRIFT['approval'])
            entity.needs.psychological.safety = self._clamp(entity.needs.psychological.safety + DEFAULT_NEED_DRIFT['safety'])
            entity.needs.psychological.power = self._clamp(entity.needs.psychological.power + DEFAULT_NEED_DRIFT['power'])
            entity.needs.psychological.freedom = self._clamp(entity.needs.psychological.freedom + DEFAULT_NEED_DRIFT['freedom'])
            entity.status.fatigue = self._clamp(entity.status.fatigue + 1.3)

    def _update_emotions(self, state: WorldState) -> None:
        for entity in state.entities.values():
            for emotion_name, decay in EMOTION_DECAY_PER_TURN.items():
                current = getattr(entity.emotions, emotion_name)
                adjusted = current - decay + (entity.status.stress / 220.0 if emotion_name in {'anger', 'sadness', 'fear'} else 0.0)
                setattr(entity.emotions, emotion_name, self._clamp(adjusted))

    def _need_scores(self, entity: Any) -> dict[str, float]:
        needs = {
            'hunger': entity.needs.survival.hunger,
            'thirst': entity.needs.survival.thirst,
            'sleepiness': entity.needs.survival.sleepiness,
            'health': 100.0 - entity.needs.survival.health,
            'sexual_desire': entity.needs.reproduction.sexual_desire,
            'intimacy': entity.needs.reproduction.intimacy,
            'belonging': entity.needs.psychological.belonging,
            'approval': entity.needs.psychological.approval,
            'safety': entity.needs.psychological.safety,
            'power': entity.needs.psychological.power,
            'freedom': entity.needs.psychological.freedom,
        }
        return {name: round(value * NEED_PRIORITY_WEIGHTS[name], 4) for name, value in needs.items()}

    def list_target_options(self, state: WorldState, actor_id: str) -> list[dict[str, str]]:
        actor = state.entities[actor_id]
        target_options: list[dict[str, str]] = []
        for entity_id, target in state.entities.items():
            if entity_id == actor_id:
                continue
            same_location = target.status.current_location_id == actor.status.current_location_id
            relation = state.get_relation(actor_id, entity_id)
            relation_hint = relation.trend if relation is not None else 'unknown'
            target_options.append({
                'entity_id': entity_id,
                'name': target.name.full_name,
                'location_id': target.status.current_location_id,
                'same_location': 'yes' if same_location else 'no',
                'relation_hint': relation_hint,
            })
        return target_options

    def _pick_target(self, state: WorldState, actor_id: str) -> str | None:
        actor = state.entities[actor_id]
        best_target: str | None = None
        best_score = -999999.0
        for entity_id, target in state.entities.items():
            if entity_id == actor_id:
                continue
            relation = state.get_relation(actor_id, entity_id)
            location = state.locations.get(target.status.current_location_id)
            proximity_bonus = 12.0 if target.status.current_location_id == actor.status.current_location_id else 0.0
            relation_score = 0.0
            if relation is not None:
                relation_score = (
                    relation.extended.interest
                    + relation.basic.like * 0.8
                    + relation.basic.trust * 0.6
                    + relation.basic.suspicion * 0.45
                    + relation.advanced.obsession * 0.8
                    + relation.advanced.resentment * 0.6
                    + relation.advanced.exclusivity * 0.35
                )
            world_bonus = (location.rumor_spread_rate * 0.06 if location else 0.0)
            candidate_score = relation_score + proximity_bonus + world_bonus
            if candidate_score > best_score:
                best_score = candidate_score
                best_target = entity_id
        return best_target

    def _engine_bias(self, actor: Any, action_type: str) -> float:
        affinity = ACTION_ENGINE_AFFINITY[action_type]
        style = actor.style_ratio
        intensity = actor.intensity
        return (
            style.action * intensity.action * affinity['action']
            + style.inner * intensity.inner * affinity['inner']
            + style.cognition * intensity.cognition * affinity['cognition']
            + style.world * intensity.world * affinity['world']
        ) / 100.0

    def _ideology_bias(self, actor: Any, action_type: str) -> float:
        favored = ACTION_IDEOLOGY_BIAS.get(action_type, set())
        values = {value.lower() for value in actor.ideology.core_values}
        taboo = {value.lower() for value in actor.ideology.taboo_values}
        hits = sum(1 for item in favored if item.lower() in values)
        taboo_hits = sum(1 for item in favored if item.lower() in taboo)
        return hits * 2.4 - taboo_hits * 1.6

    def _long_term_pressure(self, state: WorldState, actor_id: str, target_id: str | None) -> tuple[float, float]:
        if not target_id:
            return 0.0, 0.0
        memory = state.get_relation_memory(actor_id, target_id)
        support = float(memory.get('support_balance', 0.0))
        charge = float(memory.get('long_term_charge', 0.0))
        breaches = float(memory.get('breach_count', 0))
        return support + charge * 0.4, breaches * 2.1

    def _candidate_actions(self, state: WorldState, actor_id: str, *, forced_target_id: str | None = None) -> list[dict[str, Any]]:
        actor = state.entities[actor_id]
        target_id = forced_target_id or self._pick_target(state, actor_id)
        needs = self._need_scores(actor)
        top_need, top_need_score = max(needs.items(), key=lambda item: item[1])
        location = state.locations.get(actor.status.current_location_id)
        relation = state.get_relation(actor_id, target_id) if target_id else None
        privacy = location.privacy_level if location else 0.0
        social_pressure = location.social_pressure if location else 0.0
        rumor_rate = location.rumor_spread_rate if location else 0.0
        target_like = relation.basic.like if relation else 0.0
        target_trust = relation.basic.trust if relation else 0.0
        target_suspicion = relation.basic.suspicion if relation else 0.0
        target_attachment = relation.extended.attachment if relation else 0.0
        target_dependence = relation.extended.dependence if relation else 0.0
        target_obsession = relation.advanced.obsession if relation else 0.0
        actor_power = SOCIAL_POSITION_POWER.get(actor.status.social_position, 50.0)
        long_term_support, long_term_breach = self._long_term_pressure(state, actor_id, target_id)
        candidates: list[dict[str, Any]] = []

        def add(action_type: str, short_term: float, long_term: float, world_cost: float, reason: str) -> None:
            engine_bias = self._engine_bias(actor, action_type)
            ideology_bias = self._ideology_bias(actor, action_type)
            pressure_profile = self.world_pressure_engine.evaluate_action_pressure(
                state,
                actor_id,
                action_type,
                target_id=target_id,
                location_id=actor.status.current_location_id,
            )
            adjusted_world_cost = world_cost + pressure_profile.pressure_score * 0.55
            total = short_term * 0.62 + long_term * 0.28 + engine_bias + ideology_bias - adjusted_world_cost + pressure_profile.privacy_shield * 0.08
            candidates.append(
                {
                    'actor_id': actor_id,
                    'target_id': target_id,
                    'location_id': actor.status.current_location_id,
                    'top_need': top_need,
                    'need_score': round(top_need_score, 4),
                    'action_type': action_type,
                    'short_term_score': round(short_term, 4),
                    'long_term_score': round(long_term, 4),
                    'world_cost': round(adjusted_world_cost, 4),
                    'engine_bias': round(engine_bias, 4),
                    'ideology_bias': round(ideology_bias, 4),
                    'score': round(total, 4),
                    'reason': reason,
                    'world_pressure_preview': {
                        'pressure_score': pressure_profile.pressure_score,
                        'visibility_risk': pressure_profile.visibility_risk,
                        'hierarchy_friction': pressure_profile.hierarchy_friction,
                        'privacy_shield': pressure_profile.privacy_shield,
                    },
                }
            )

        add('observe', needs['approval'] * 0.18 + target_suspicion * 0.22 + actor.intensity.cognition * 0.30, 7.0 + long_term_breach * 0.45, rumor_rate * 0.02, 'information_gain')
        add('approach', needs['belonging'] * 0.40 + target_like * 0.25 + target_trust * 0.18 + actor.emotions.affection * 0.16, 10.0 + long_term_support * 0.8, social_pressure * 0.02, 'social_pull')
        add('support', needs['belonging'] * 0.32 + needs['approval'] * 0.24 + target_trust * 0.22 + actor.emotions.affection * 0.20, 12.0 + long_term_support * 1.2, rumor_rate * 0.04, 'bond_support')
        add('withdraw', needs['safety'] * 0.52 + actor.emotions.fear * 0.48 + target_suspicion * 0.20, 8.0 - long_term_support * 0.4 + long_term_breach * 0.7, max(0.0, privacy - social_pressure) * 0.03, 'defensive_need')
        add('confront', needs['power'] * 0.70 + actor.emotions.anger * 0.70 + target_suspicion * 0.36 + actor.intensity.action * 0.22 + actor.inner_profile.pride * 0.20 - actor.emotions.fear * 0.14, 6.0 - long_term_support * 0.5 + long_term_breach * 1.6 + actor_power * 0.06, social_pressure * 0.03 + max(0.0, 50.0 - actor_power) * 0.05, 'conflict_pressure')
        add('confide', needs['intimacy'] * 0.58 + privacy * 0.25 + target_trust * 0.46 + actor.emotions.affection * 0.34 + target_attachment * 0.22 - social_pressure * 0.12, 16.0 + long_term_support * 1.5 + target_trust * 0.12, max(0.0, rumor_rate - privacy) * 0.06, 'private_disclosure')
        add('seek_help', needs['health'] * 0.62 + needs['safety'] * 0.48 + actor.status.injury * 0.56 + actor.status.stress * 0.25 + target_trust * 0.20 + target_dependence * 0.16, 12.0 + long_term_support * 1.1, social_pressure * 0.05, 'stability_recovery')
        add('wait', 5.0 + actor.intensity.world * 0.12 + social_pressure * 0.08 + target_obsession * 0.03, 4.0 + long_term_breach * 0.4, 0.0, 'default_hold')
        return sorted(candidates, key=lambda item: item['score'], reverse=True)

    def list_action_options(self, state: WorldState, actor_id: str, *, target_id: str | None = None) -> list[dict[str, Any]]:
        candidates = self._candidate_actions(state, actor_id, forced_target_id=target_id)
        return [
            {
                'actor_id': candidate['actor_id'],
                'target_id': candidate['target_id'],
                'location_id': candidate['location_id'],
                'action_type': candidate['action_type'],
                'top_need': candidate['top_need'],
                'score': candidate['score'],
                'reason': candidate['reason'],
                'world_cost': candidate['world_cost'],
                'pressure_score': candidate['world_pressure_preview']['pressure_score'],
            }
            for candidate in candidates
        ]

    def _resolve_action(self, state: WorldState, actor_id: str, choice: PlayerTurnChoice | None = None) -> dict[str, Any]:
        forced_target_id = choice.target_id if choice else None
        candidates = self._candidate_actions(state, actor_id, forced_target_id=forced_target_id)
        if choice is None:
            selected = candidates[0]
        else:
            selected = next((item for item in candidates if item['action_type'] == choice.action_type), None)
            if selected is None:
                available = ', '.join(item['action_type'] for item in candidates)
                raise ValueError(f"Unsupported action_type={choice.action_type} for actor={actor_id}. available={available}")
        selected['candidate_preview'] = [
            {
                'action_type': item['action_type'],
                'score': item['score'],
                'short_term_score': item['short_term_score'],
                'long_term_score': item['long_term_score'],
                'world_cost': item['world_cost'],
                'pressure_score': item['world_pressure_preview']['pressure_score'],
            }
            for item in candidates[:6]
        ]
        selected['is_player_selected'] = choice is not None
        return selected

    def _apply_actor_effects(self, state: WorldState, action: dict[str, Any]) -> None:
        actor = state.entities[action['actor_id']]
        action_type = action['action_type']
        if action_type in {'approach', 'support', 'confide'}:
            actor.needs.psychological.belonging = self._clamp(actor.needs.psychological.belonging - 1.8)
            actor.needs.reproduction.intimacy = self._clamp(actor.needs.reproduction.intimacy - 1.2)
            actor.emotions.affection = self._clamp(actor.emotions.affection + 0.8)
        elif action_type == 'withdraw':
            actor.needs.psychological.safety = self._clamp(actor.needs.psychological.safety - 1.5)
            actor.status.stress = self._clamp(actor.status.stress - 0.9)
        elif action_type == 'confront':
            actor.needs.psychological.power = self._clamp(actor.needs.psychological.power - 1.4)
            actor.emotions.anger = self._clamp(actor.emotions.anger - 0.5)
            actor.status.stress = self._clamp(actor.status.stress + 0.8)
        elif action_type == 'seek_help':
            actor.needs.psychological.safety = self._clamp(actor.needs.psychological.safety - 1.8)
            actor.status.stress = self._clamp(actor.status.stress - 1.3)
        elif action_type == 'observe':
            actor.emotions.fear = self._clamp(actor.emotions.fear - 0.2)
        actor.status.fatigue = self._clamp(actor.status.fatigue + 0.3)

    def _build_highlights(self, state: WorldState, actions: list[dict[str, Any]], secret_events: list[dict[str, Any]], secondary_events: list[dict[str, Any]]) -> list[str]:
        highlights: list[str] = []
        if actions:
            strongest = max(actions, key=lambda item: item['score'])
            highlights.append(f"{state.entities[strongest['actor_id']].name.full_name} が {strongest['action_type']} を選択")
        for event in secret_events[:2]:
            secret = state.secrets.get(event['secret_id'])
            if secret:
                highlights.append(f"秘密が進展: {secret.title} ({event['new_visibility']})")
        for event in secondary_events[:3]:
            highlights.append(event['summary'])
        return highlights


    def _build_turn_trace(self, state: WorldState, actions: list[dict[str, Any]], secret_events: list[dict[str, Any]], secondary_events: list[dict[str, Any]]) -> dict[str, Any]:
        action_chain: list[dict[str, Any]] = []
        for action in actions:
            actor_name = state.entities[action['actor_id']].name.full_name
            target_name = state.entities[action['target_id']].name.full_name if action.get('target_id') and action.get('target_id') in state.entities else None
            action_chain.append({
                'actor_id': action['actor_id'],
                'actor_name': actor_name,
                'action_type': action['action_type'],
                'target_id': action.get('target_id'),
                'target_name': target_name,
                'score': round(float(action.get('score', 0.0)), 4),
                'top_need': action.get('top_need'),
                'reason': action.get('reason'),
                'world_cost': round(float(action.get('world_cost', 0.0)), 4),
                'consequence_count': len(action.get('world_events', [])),
            })

        return {
            'turn': state.turn,
            'world_tension': round(state.world_tension, 4),
            'action_chain': action_chain,
            'secret_chain': list(secret_events),
            'secondary_chain': list(secondary_events),
            'hot_locations': sorted(
                ({'location_id': key, 'heat': round(value, 4)} for key, value in state.location_heat.items()),
                key=lambda item: item['heat'],
                reverse=True,
            )[:3],
        }

    def run_turn(self, state: WorldState, *, player_choices: Mapping[str, PlayerTurnChoice] | None = None) -> TurnResult:
        state.turn += 1
        self._update_needs(state)
        self._update_emotions(state)
        self.relation_manager.apply_turn_decay(state)

        actions: list[dict[str, Any]] = []
        secret_events: list[dict[str, Any]] = []
        for actor_id in state.entities:
            choice = player_choices.get(actor_id) if player_choices else None
            action = self._resolve_action(state, actor_id, choice)
            self._apply_actor_effects(state, action)
            relation_result = self.relation_manager.apply_action(state, action)
            action['relation_pairs_updated'] = relation_result.changed_pairs
            world_events = self.world_pressure_engine.apply_action_fallout(state, action)
            reputation_events = self.reputation_manager.apply_public_reputation_shift(state, action)
            hierarchy_events = self.hierarchy_manager.apply_hierarchy_response(state, action)
            faction_events = self.faction_manager.apply_group_pressure(state, action)
            action['world_events'] = world_events + reputation_events + hierarchy_events + faction_events
            actions.append(action)
            state.log_event('action', action)
            for payload in action['world_events']:
                state.log_event(payload['trigger_type'], payload)

            for exposure in self.secret_exposure_engine.evaluate_action(state, action):
                payload = {
                    'secret_id': exposure.secret_id,
                    'old_visibility': exposure.old_visibility,
                    'new_visibility': exposure.new_visibility,
                    'reason': exposure.reason,
                    'affected_entities': exposure.affected_entities,
                }
                secret_events.append(payload)
                state.revealed_secrets.append(payload)
                state.log_event('secret_exposure', payload)

        secondary_events = self.secondary_reaction_engine.process_turn(state, actions, secret_events)
        passive_world_events = self.world_pressure_engine.apply_passive_world_drift(state)
        offscreen_events = self.offscreen_event_engine.process_turn(state)
        for payload in passive_world_events:
            state.log_event('world_drift', payload)
        secondary_events.extend(passive_world_events)
        secondary_events.extend(offscreen_events)
        state.secondary_events = list(secondary_events)
        state.last_actions = actions
        state.turn_traces.append(self._build_turn_trace(state, actions, secret_events, secondary_events))
        if len(state.turn_traces) > 200:
            state.turn_traces = state.turn_traces[-200:]
        highlights = self._build_highlights(state, actions, secret_events, secondary_events)
        return TurnResult(
            turn=state.turn,
            actions=actions,
            highlights=highlights,
            secret_events=secret_events,
            secondary_events=secondary_events,
        )
