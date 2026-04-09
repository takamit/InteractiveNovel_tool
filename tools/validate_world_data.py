from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.logic.application import create_app
from core.services.persistence.json_loader import WorldDataLoader


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    loader = WorldDataLoader(project_root)
    loader.validate_world('sample_world')
    print('JSON / Schema / Logic validation: OK')

    app = create_app(project_root, world_name='sample_world')
    result = app.run_turns(turns=1)[0]
    print(f"MVP turn validation: OK (turn={result['turn']}, actions={result['action_count']})")


if __name__ == '__main__':
    main()
