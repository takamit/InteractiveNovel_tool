from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EmotionalProfile:
    joy: float
    anger: float
    sadness: float
    fear: float
    affection: float
