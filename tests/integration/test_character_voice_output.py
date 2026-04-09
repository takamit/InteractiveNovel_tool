from pathlib import Path

from core.logic.runtime.engine import SimulationEngine
from ui.components.play.dialogue_renderer import EmotionDialogueRenderer


def test_character_specific_support_lines_are_distinct() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root)
    state = engine.bootstrap()
    renderer = EmotionDialogueRenderer()

    yuu_line = renderer.render_spoken_line(
        state,
        {
            'actor_id': 'char_002',
            'target_id': 'char_001',
            'action_type': 'support',
            'location_id': 'loc_classroom_2a',
        },
    )
    jin_line = renderer.render_spoken_line(
        state,
        {
            'actor_id': 'char_003',
            'target_id': 'char_001',
            'action_type': 'support',
            'location_id': 'loc_hallway_2f',
        },
    )

    assert yuu_line is not None and '勘違いはしないで' in yuu_line
    assert jin_line is not None and '無駄にするなよ' in jin_line
    assert yuu_line != jin_line


def test_choice_prompt_reflects_actor_style() -> None:
    project_root = Path(__file__).resolve().parents[2]
    engine = SimulationEngine(project_root=project_root)
    state = engine.bootstrap()
    renderer = EmotionDialogueRenderer()

    option = {
        'action_type': 'confide',
        'target_id': 'char_001',
        'top_need': 'intimacy',
    }
    akane_prompt = renderer.choice_prompt(state, 'char_006', option)
    sara_prompt = renderer.choice_prompt(state, 'char_007', option)

    assert '誤魔化しを混ぜながら本音を落とす' in akane_prompt
    assert '壊れそうなまま依存を零す' in sara_prompt
