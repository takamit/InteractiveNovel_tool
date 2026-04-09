from __future__ import annotations

from pathlib import Path

from core.logic.runtime.engine import SimulationEngine
from core.logic.environment.location_manager import WorldPressureEngine
from core.logic.secrets.exposure_engine import SecretExposureEngine


def test_turn_flow_and_save_load() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root, world_name='sample_world')
    engine.bootstrap()

    result = engine.run_turn()
    assert result.turn == 1
    assert len(result.actions) == 8
    assert all('candidate_preview' in action for action in result.actions)
    assert all('relation_pairs_updated' in action for action in result.actions)
    assert all('world_events' in action for action in result.actions)
    assert isinstance(result.secondary_events, list)

    save_path = engine.save(slot_name='slot_02')
    assert save_path.exists()

    loaded = engine.load_snapshot(save_path)
    assert loaded.turn == 1
    assert len(loaded.entities) == 8
    assert isinstance(loaded.secondary_events, list)
    assert isinstance(loaded.location_pressure_history, list)
    assert isinstance(loaded.offscreen_events, list)


def test_secret_trigger_reveals_private_axis() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root, world_name='sample_world')
    state = engine.bootstrap()

    relation = state.get_relation('char_001', 'char_002')
    assert relation is not None
    relation.basic.trust = 40.0
    state.entities['char_001'].status.current_location_id = 'loc_rooftop_access'

    exposure_engine = SecretExposureEngine()
    events = exposure_engine.evaluate_action(
        state,
        {
            'actor_id': 'char_001',
            'target_id': 'char_002',
            'action_type': 'confide',
            'location_id': 'loc_rooftop_access',
        },
    )

    assert any(event.secret_id == 'secret_001' and event.new_visibility == 'revealed' for event in events)
    assert state.secrets['secret_001'].visibility == 'revealed'


def test_viewpoint_renderer_hides_unknown_secret() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root, world_name='sample_world')
    state = engine.bootstrap()

    relation = state.get_relation('char_001', 'char_002')
    assert relation is not None
    relation.basic.trust = 40.0
    state.entities['char_001'].status.current_location_id = 'loc_rooftop_access'

    engine.run_turn()
    omniscient = engine.render_latest_turn(mode='omniscient')
    protagonist = engine.render_latest_turn(mode='protagonist')

    assert 'SECRET' in omniscient
    assert 'secret=' not in protagonist


def test_secondary_reaction_changes_state() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root, world_name='sample_world')
    state = engine.bootstrap()

    start_stress = state.entities['char_008'].status.stress
    exposure_engine = SecretExposureEngine()
    events = exposure_engine.evaluate_action(
        state,
        {
            'actor_id': 'char_005',
            'target_id': 'char_008',
            'action_type': 'confront',
            'location_id': 'loc_student_council',
        },
    )
    payloads = [
        {
            'secret_id': event.secret_id,
            'old_visibility': event.old_visibility,
            'new_visibility': event.new_visibility,
            'reason': event.reason,
            'affected_entities': event.affected_entities,
        }
        for event in events
    ]
    secondary = engine.turn_manager.secondary_reaction_engine.process_turn(state, [], payloads)

    assert any(item['trigger_id'] == 'secret_003' for item in secondary)
    assert state.entities['char_008'].status.stress > start_stress


def test_world_pressure_public_confront_is_harsher_than_private_confide() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root, world_name='sample_world')
    state = engine.bootstrap()
    pressure_engine = WorldPressureEngine()

    public_profile = pressure_engine.evaluate_action_pressure(
        state,
        'char_003',
        'confront',
        target_id='char_001',
        location_id='loc_hallway_2f',
    )
    private_profile = pressure_engine.evaluate_action_pressure(
        state,
        'char_001',
        'confide',
        target_id='char_002',
        location_id='loc_rooftop_access',
    )

    assert public_profile.pressure_score > private_profile.pressure_score
    assert public_profile.visibility_risk > private_profile.visibility_risk


def test_world_pressure_fallout_updates_tension_and_heat() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root, world_name='sample_world')
    state = engine.bootstrap()
    pressure_engine = WorldPressureEngine()

    action = {
        'actor_id': 'char_003',
        'target_id': 'char_001',
        'action_type': 'confront',
        'location_id': 'loc_hallway_2f',
    }
    emitted = pressure_engine.apply_action_fallout(state, action)

    assert state.world_tension > 0.0
    assert state.location_heat['loc_hallway_2f'] > 0.0
    assert state.location_pressure_history
    assert 'world_pressure' in action
    assert isinstance(emitted, list)


def test_social_pressure_and_offscreen_events_are_generated() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root, world_name='sample_world')
    engine.bootstrap()
    result = engine.run_turn()

    assert any(evt.get('trigger_type') in {'faction_pressure', 'reputation_shift', 'hierarchy_sanction', 'hierarchy_cover', 'offscreen_rumor_echo', 'offscreen_secret_drift', 'offscreen_institution_notice'} for evt in result.secondary_events + [e for a in result.actions for e in a['world_events']])
    assert isinstance(engine.state.offscreen_events, list)
    assert isinstance(engine.state.faction_climate, dict)


def test_analysis_report_includes_social_layers() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root, world_name='sample_world')
    engine.bootstrap()
    engine.run_turn()
    report = engine.analysis_report()

    assert 'faction_climate' in report
    assert 'institution_pressure' in report
    assert 'offscreen_event_count' in report
