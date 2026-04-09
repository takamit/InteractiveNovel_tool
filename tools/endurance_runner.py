from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.logic.application import create_app


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    app = create_app(project_root)
    app.run_turns(turns=20, autosave=False)
    print(json.dumps(app.analysis(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
