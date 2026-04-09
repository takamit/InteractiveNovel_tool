from __future__ import annotations

import json
from pathlib import Path

from core.logic.application import create_app


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    app = create_app(project_root)
    app.run_turns(turns=1, autosave=False)
    print(json.dumps(app.analysis().get('hottest_relations', []), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
