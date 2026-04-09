from __future__ import annotations

import json
from pathlib import Path

from core.logic.runtime.world_state import WorldState


class HandoffExporter:
    def export_summary(self, state: WorldState, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.write_text(json.dumps({'world_id': state.world_id, 'turn': state.turn, 'world_tension': state.world_tension}, ensure_ascii=False, indent=2), encoding='utf-8')
        return output_path
