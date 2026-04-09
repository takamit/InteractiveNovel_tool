from __future__ import annotations

import json
from typing import Any


class StructuredResponseParser:
    def parse_json(self, text: str) -> dict[str, Any]:
        return json.loads(text)
