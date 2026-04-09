from __future__ import annotations

from pathlib import Path
from typing import Any

from core.models.simulation_context import SimulationContext
from core.logic.runtime.turn_manager import PlayerTurnChoice, TurnManager, TurnResult
from core.logic.runtime.world_state import WorldState
from core.logic.experience.output_formatter import WorldViewRenderer
from core.services.persistence.json_loader import WorldDataLoader
from core.services.persistence.save_manager import SaveManager
from core.logic.quality.diagnostics import ReleaseDiagnostics
from core.logic.quality.endurance_auditor import EnduranceAuditor


class SimulationEngine:
    def __init__(self, project_root: str | Path, world_name: str = 'sample_world') -> None:
        self.project_root = Path(project_root)
        self.world_name = world_name
        self.loader = WorldDataLoader(self.project_root)
        self.turn_manager = TurnManager()
        self.save_manager = SaveManager(self.project_root)
        self.context = SimulationContext(world_name=world_name)
        self.renderer = WorldViewRenderer()
        self.release_diagnostics = ReleaseDiagnostics()
        self.endurance_auditor = EnduranceAuditor()
        self.state: WorldState | None = None
        self.last_turn_result: TurnResult | None = None

    def bootstrap(self) -> WorldState:
        models = self.loader.load_world_models(self.world_name)
        self.state = WorldState.from_models(
            entities=models['entities'],
            relations=models['relations'],
            secrets=models['secrets'],
            locations=models['locations'],
            turn=self.context.current_turn,
        )
        return self.state

    def _ensure_state(self) -> WorldState:
        if self.state is None:
            self.bootstrap()
        assert self.state is not None
        return self.state

    def list_target_options(self, *, player_entity_id: str) -> list[dict[str, str]]:
        state = self._ensure_state()
        return self.turn_manager.list_target_options(state, player_entity_id)

    def list_player_options(self, *, player_entity_id: str, target_id: str | None = None) -> list[dict[str, Any]]:
        state = self._ensure_state()
        return self.turn_manager.list_action_options(state, player_entity_id, target_id=target_id)

    def run_turn(self, *, autosave: bool = False) -> TurnResult:
        state = self._ensure_state()
        result = self.turn_manager.run_turn(state)
        self.context.current_turn = result.turn
        self.last_turn_result = result
        if autosave:
            self.save_manager.save(self.state, slot_name='autosave')
        return result

    def run_player_turn(
        self,
        *,
        player_entity_id: str,
        action_type: str,
        target_id: str | None = None,
        autosave: bool = False,
    ) -> TurnResult:
        state = self._ensure_state()
        player_choice = PlayerTurnChoice(actor_id=player_entity_id, action_type=action_type, target_id=target_id)
        result = self.turn_manager.run_turn(state, player_choices={player_entity_id: player_choice})
        self.context.current_turn = result.turn
        self.last_turn_result = result
        if autosave:
            self.save_manager.save(self.state, slot_name='autosave')
        return result

    def save(self, *, slot_name: str = 'slot_01') -> Path:
        self._ensure_state()
        assert self.state is not None
        return self.save_manager.save(self.state, slot_name=slot_name)

    def load_snapshot(self, snapshot_path: str | Path) -> WorldState:
        self.state = self.save_manager.load(snapshot_path)
        self.context.current_turn = self.state.turn
        return self.state

    def render_latest_turn(self, *, mode: str = 'omniscient', focal_entity_id: str | None = None) -> str:
        if self.state is None or self.last_turn_result is None:
            raise RuntimeError('No turn has been executed yet.')
        return self.renderer.render_turn(self.state, self.last_turn_result, mode=mode, focal_entity_id=focal_entity_id)

    def analysis_report(self) -> dict[str, Any]:
        state = self._ensure_state()
        highest_stress = sorted(
            (
                {
                    'entity_id': entity.id,
                    'name': entity.name.full_name,
                    'stress': round(entity.status.stress, 4),
                    'rumor_level': round(entity.status.rumor_level, 4),
                }
                for entity in state.entities.values()
            ),
            key=lambda item: (item['stress'], item['rumor_level']),
            reverse=True,
        )[:5]
        hottest_relations = sorted(
            (
                {
                    'pair': key,
                    'charge': round(float(value.get('long_term_charge', 0.0)), 4),
                    'breaches': int(value.get('breach_count', 0)),
                    'touch_streak': round(float(value.get('touch_streak', 0.0)), 4),
                }
                for key, value in state.relation_memories.items()
            ),
            key=lambda item: (item['charge'], item['breaches'], item['touch_streak']),
            reverse=True,
        )[:5]
        hottest_locations = sorted(
            (
                {
                    'location_id': key,
                    'heat': round(value, 4),
                }
                for key, value in state.location_heat.items()
            ),
            key=lambda item: item['heat'],
            reverse=True,
        )[:5]
        return {
            'turn': state.turn,
            'summary': state.summary(),
            'highest_stress': highest_stress,
            'hottest_relations': hottest_relations,
            'world_tension': round(state.world_tension, 4),
            'hottest_locations': hottest_locations,
            'location_pressure_events': len(state.location_pressure_history),
            'save_metadata': dict(state.save_metadata),
            'faction_climate': {key: round(value, 4) for key, value in state.faction_climate.items()},
            'institution_pressure': round(state.institution_pressure, 4),
            'offscreen_event_count': len(state.offscreen_events),
            'recent_offscreen_events': list(state.offscreen_events[-3:]),
            'player_ready': True,
            'recent_turn_traces': list(state.turn_traces[-3:]),
        }

    def snapshot(self) -> dict[str, Any]:
        state = self._ensure_state()
        return state.summary()

    def release_report(self) -> dict[str, Any]:
        state = self._ensure_state()
        report = self.release_diagnostics.build_report(state)
        report['recent_turn_traces'] = list(state.turn_traces[-3:])
        return report

    def endurance_report(self, snapshots: list[dict[str, Any]]) -> dict[str, Any]:
        state = self._ensure_state()
        return self.endurance_auditor.build_report(snapshots, state)
