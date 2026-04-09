from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class WorldDataWriter:
    def write_json(self, path: str | Path, payload: dict[str, Any]) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        return target


JsonSaver = WorldDataWriter
