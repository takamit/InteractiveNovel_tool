from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.logic.application import create_app
from ui.cli.main_cli import SimulationCliRunner
from ui.desktop.app import SimulationDesktopRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="対話式小説シミュレーター")
    parser.add_argument("--mode", choices=["cli", "gui", "auto"], default="cli", help="起動モード")
    parser.add_argument("--world", default="sample_world", help="読み込むワールド名")
    parser.add_argument("--player", default="char_001", help="プレイヤーエンティティID")
    parser.add_argument("--turns", type=int, default=1, help="CLI/autoモードの実行ターン数")
    parser.add_argument("--autosave", action="store_true", help="ターン実行後に自動保存する")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    project_root = Path(__file__).resolve().parent

    if args.mode == "gui":
        SimulationDesktopRunner().run(project_root=project_root, player_entity_id=args.player)
        return

    if args.mode == "cli":
        SimulationCliRunner().run(project_root=project_root, player_entity_id=args.player, turns=args.turns)
        return

    app = create_app(project_root=project_root, world_name=args.world)
    app.run_turns(turns=args.turns, autosave=args.autosave)
    print(app.render(mode="omniscient"))
    print()
    print(app.render(mode="protagonist", focal_entity_id=args.player))
    print()
    print(json.dumps(app.analysis(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
