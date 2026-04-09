from __future__ import annotations

from core.logic.runtime.world_state import WorldState


class NovelRenderer:
    def render_summary(self, state: WorldState) -> str:
        actions = state.last_actions[-3:]
        lines = [f'Turn {state.turn}']
        for action in actions:
            lines.append(f"- {action['actor_id']} -> {action['action_type']}")
        return '
'.join(lines)
