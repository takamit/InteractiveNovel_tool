from __future__ import annotations

from pathlib import Path
from typing import Callable

from core.logic.application import create_app
from ui.cli.menus import CliMenuBuilder


class SimulationCliRunner:
    def __init__(self, *, input_func: Callable[[str], str] = input, output_func: Callable[[str], None] = print) -> None:
        self.input_func = input_func
        self.output_func = output_func

    def _print_options(self, options: list[dict[str, object]]) -> None:
        for option in options:
            self.output_func(f"{option['index']}. {option['choice_label']}")
            self.output_func(f"   {option['choice_detail']}")

    def _safe_pick(self, prompt: str, maximum: int, *, default: int) -> int:
        raw = self.input_func(prompt).strip()
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError:
            self.output_func(f"数値で入力してちょうだい。既定値 {default} を使うわ。")
            return default
        if value < 0 or value > maximum:
            self.output_func(f"範囲外よ。既定値 {default} を使うわ。")
            return default
        return value

    def run(self, project_root: str | Path, *, player_entity_id: str = 'char_001', turns: int = 1) -> str:
        app = create_app(project_root)
        commands = ', '.join(command.name for command in CliMenuBuilder().default_commands())
        self.output_func(f'CLI ready: {commands}')
        for _ in range(turns):
            targets = app.list_target_options(player_entity_id)
            self.output_func('[相手]')
            self.output_func('0. 流れに任せる')
            for index, target in enumerate(targets, start=1):
                same_loc = '今いる場所にいる' if target['same_location'] == 'yes' else '別の場所にいる'
                self.output_func(f"{index}. {target['name']}｜{same_loc}｜{target['relation_hint']}")
            target_index = self._safe_pick('target> ', len(targets), default=0)
            target_id = None if target_index == 0 else targets[target_index - 1]['entity_id']

            options = app.list_presented_player_options(player_entity_id, target_id=target_id)
            self.output_func('[行動]')
            self._print_options(options)
            action_index = self._safe_pick('action> ', len(options), default=1)
            selected = options[action_index - 1]
            app.run_player_turn(
                player_entity_id=player_entity_id,
                action_type=str(selected['action_type']),
                target_id=target_id or (str(selected['target_id']) if selected.get('target_id') else None),
            )
            self.output_func(app.render(mode='protagonist', focal_entity_id=player_entity_id))
            self.output_func('-' * 72)
            self.output_func(app.render(mode='analyst', focal_entity_id=player_entity_id))
        return f'CLI ready: {commands} | turn={app.analysis()["turn"]}'


InteractiveCliRunner = SimulationCliRunner
CliApplication = SimulationCliRunner
