from __future__ import annotations

from enum import Enum


class OutputMode(str, Enum):
    PLAY = "play"
    ANALYSIS = "analysis"
    DEBUG = "debug"
