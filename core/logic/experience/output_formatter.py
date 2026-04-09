from __future__ import annotations

from typing import Any

from core.logic.runtime.world_state import WorldState
from core.logic.experience.mode_manager import DEFAULT_FOCAL_ENTITY, ViewMode
from ui.components.modes import OutputMode
from ui.components.output_router import OutputRouter
from ui.components.play.narrative_renderer import NarrativeRenderer


class WorldViewRenderer:
    def __init__(self) -> None:
        self.narrative_renderer = NarrativeRenderer()

    def _name(self, state: WorldState, entity_id: str | None) -> str:
        if not entity_id:
            return '不明'
        entity = state.entities.get(entity_id)
        return entity.name.full_name if entity else entity_id

    def _resolve_focal(self, mode: ViewMode, focal_entity_id: str | None) -> str | None:
        if mode == 'character':
            return focal_entity_id
        return DEFAULT_FOCAL_ENTITY.get(mode, focal_entity_id)

    def _is_visible_to_focal(self, state: WorldState, action: dict[str, Any], focal_id: str | None) -> bool:
        if focal_id is None or focal_id not in state.entities:
            return True
        if action['actor_id'] == focal_id or action.get('target_id') == focal_id:
            return True
        return state.entities[focal_id].status.current_location_id == action['location_id']

    def _render_action_line(self, state: WorldState, action: dict[str, Any], mode: ViewMode, focal_id: str | None) -> list[str]:
        actor_name = self._name(state, action['actor_id'])
        target_name = self._name(state, action.get('target_id')) if action.get('target_id') else None
        location = state.locations.get(action['location_id'])
        location_name = location.name if location else action['location_id']
        if mode in {'protagonist', 'observer', 'character'} and not self._is_visible_to_focal(state, action, focal_id):
            return []

        if mode == 'analyst':
            preview = ', '.join(
                f"{item['action_type']}:{item['score']:.1f}|S{item['short_term_score']:.1f}|L{item['long_term_score']:.1f}"
                for item in action.get('candidate_preview', [])
            )
            return [
                (
                    f"- {actor_name} -> {action['action_type']} / target={target_name or 'なし'} / need={action['top_need']} "
                    f"/ reason={action['reason']} / engine={action['engine_bias']:.1f} / ideology={action['ideology_bias']:.1f} / candidates=[{preview}]"
                )
            ]

        if mode == 'omniscient':
            if target_name:
                return [f"- {actor_name} は {location_name} で {target_name} に {action['action_type']} を選んだ。"]
            return [f"- {actor_name} は {location_name} で {action['action_type']} を選んだ。"]

        return [f"- {line}" for line in self.narrative_renderer.render_action(state, action, mode=mode, focal_id=focal_id)]

    def _render_secret_line(self, state: WorldState, event: dict[str, Any], mode: ViewMode, focal_id: str | None) -> str | None:
        secret = state.secrets.get(event['secret_id'])
        if secret is None:
            return None

        if mode == 'omniscient':
            return f"- SECRET {secret.title}: {event['old_visibility']} → {event['new_visibility']}"
        if mode == 'analyst':
            pressure = state.secret_pressure.get(secret.id, 0.0)
            return f"- secret={secret.id} visibility={event['new_visibility']} pressure={pressure:.1f} affected={','.join(event['affected_entities'])}"

        if focal_id is None:
            return None
        knowledge = secret.knowledge_states.get(focal_id, 'unknown')
        if knowledge == 'unknown':
            return None
        if knowledge == 'rumored':
            return f"- まだ輪郭しか見えない。それでも、{secret.title} という名だけは残った。"
        if knowledge == 'partially_known':
            return f"- {secret.title} の断片が胸に引っかかる。"
        return f"- もう目を逸らせない。{secret.title} が現実として残った。"

    def _render_secondary_line(self, state: WorldState, event: dict[str, Any], mode: ViewMode, focal_id: str | None) -> str | None:
        if mode == 'analyst':
            return f"- reaction[{event['trigger_type']}] {event['summary']}"
        if mode == 'omniscient':
            return f"- 余波: {event['summary']}"
        if focal_id and focal_id in event.get('affected_entities', []):
            return f"- {event['summary']}"
        return None

    def render_turn(self, state: WorldState, turn_result: Any, *, mode: ViewMode = 'omniscient', focal_entity_id: str | None = None) -> str:
        focal_id = self._resolve_focal(mode, focal_entity_id)
        if focal_id and focal_id in state.entities:
            focal = state.entities[focal_id]
            location = state.locations.get(focal.status.current_location_id)
            climate = f"現在地: {location.name}" if location else ''
            title = f"TURN {turn_result.turn} / {focal.name.full_name}" if mode != 'analyst' else f"TURN {turn_result.turn} / {mode} / {focal.name.full_name}"
        else:
            climate = ''
            title = f"TURN {turn_result.turn} / {mode}"

        lines = [title]
        if climate and mode != 'analyst':
            lines.append(climate)
        elif climate:
            lines.append(f"現在地: {climate.split(': ',1)[1]}")

        if turn_result.highlights:
            lines.append('[Highlights]')
            lines.extend(f"- {line}" for line in turn_result.highlights)

        action_lines: list[str] = []
        for action in turn_result.actions:
            action_lines.extend(self._render_action_line(state, action, mode, focal_id))
        if action_lines:
            lines.append('[Actions]')
            lines.extend(action_lines)

        secret_lines = [self._render_secret_line(state, event, mode, focal_id) for event in turn_result.secret_events]
        secret_lines = [line for line in secret_lines if line]
        if secret_lines:
            lines.append('[Secrets]')
            lines.extend(secret_lines)

        reaction_lines = [self._render_secondary_line(state, event, mode, focal_id) for event in turn_result.secondary_events]
        reaction_lines = [line for line in reaction_lines if line]
        if reaction_lines:
            lines.append('[Secondary Reactions]')
            lines.extend(reaction_lines)

        if mode == 'analyst' and focal_id and focal_id in state.entities:
            entity = state.entities[focal_id]
            lines.append('[Focal State]')
            lines.append(
                f"- stress={entity.status.stress:.1f} fatigue={entity.status.fatigue:.1f} belonging={entity.needs.psychological.belonging:.1f} affection={entity.emotions.affection:.1f} rumor={entity.status.rumor_level:.1f}"
            )

        output_mode = OutputMode.ANALYSIS if mode in {'analyst', 'omniscient'} else OutputMode.PLAY
        return OutputRouter(output_mode).route('\n'.join(lines))


TurnViewRenderer = WorldViewRenderer
