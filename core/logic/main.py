from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.logic.application import create_app


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    app = create_app(project_root, world_name='sample_world')

    print('=== 対話式小説 / 製品実装強化版 ===')
    app.run_turns(turns=1, autosave=True)
    print(app.render(mode='omniscient'))
    print()
    print(app.render(mode='protagonist'))
    print()
    print(app.render(mode='observer'))
    print()
    print(app.render(mode='analyst', focal_entity_id='char_001'))
    print()
    print('=== ANALYSIS REPORT ===')
    print(json.dumps(app.analysis(), ensure_ascii=False, indent=2))
    print()
    print('=== PLAYER OPTIONS / char_001 ===')
    print(json.dumps(app.list_player_options('char_001'), ensure_ascii=False, indent=2))
    print()
    print(f'保存先: {app.save(slot_name="slot_01")}')


if __name__ == '__main__':
    main()
