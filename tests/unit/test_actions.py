from core.logic.actions.action_generator import ActionGenerator


def test_action_generator_builds_default_set() -> None:
    candidates = ActionGenerator().generate('char_001', target_id='char_002', location_id='loc_classroom_2a')
    assert len(candidates) >= 8
    assert candidates[0].actor_id == 'char_001'
