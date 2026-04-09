from __future__ import annotations

from typing import Literal

ViewMode = Literal['omniscient', 'protagonist', 'observer', 'analyst', 'character']

DEFAULT_FOCAL_ENTITY = {
    'protagonist': 'char_001',
    'observer': 'char_004',
}
