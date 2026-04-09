from __future__ import annotations

from ui.cli.commands import CliCommandSpec


class CliMenuBuilder:
    def default_commands(self) -> list[CliCommandSpec]:
        return [
            CliCommandSpec('run_auto', '自動シミュレーションを実行する'),
            CliCommandSpec('run_player', 'プレイヤー介入ターンを実行する'),
            CliCommandSpec('report', '分析レポートを表示する'),
            CliCommandSpec('save', '現在状態を保存する'),
        ]
