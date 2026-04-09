from pathlib import Path

from core.logic.application import SimulationApplication
from ui.cli.main_cli import InteractiveCliRunner


def test_player_turn_uses_selected_action() -> None:
    project_root = Path(__file__).resolve().parents[2]
    app = SimulationApplication(project_root)
    app.bootstrap()
    options = app.list_player_options('char_001', target_id='char_002')
    selected = next(item for item in options if item['action_type'] == 'confide')
    result = app.run_player_turn(player_entity_id='char_001', action_type='confide', target_id='char_002')
    assert result['turn'] == 1
    assert app.engine.last_turn_result is not None
    player_action = next(action for action in app.engine.last_turn_result.actions if action['actor_id'] == 'char_001')
    assert player_action['action_type'] == selected['action_type']
    assert player_action['is_player_selected'] is True


def test_interactive_cli_runner_returns_ready_message() -> None:
    project_root = Path(__file__).resolve().parents[2]
    answers = iter(['0', '1'])
    outputs: list[str] = []
    runner = InteractiveCliRunner(input_func=lambda _prompt: next(answers), output_func=outputs.append)
    message = runner.run(project_root, turns=1)
    assert message.startswith('CLI ready:')
    assert any('[Actions]' in line for line in outputs)
