from __future__ import annotations

from statistics import mean
from typing import Iterable


def safe_mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return float(mean(values))


def normalize_ratio(values: dict[str, float], *, digits: int = 4) -> dict[str, float]:
    total = sum(values.values())
    if total <= 0:
        return {key: 0.0 for key in values}
    normalized = {key: round(value / total, digits) for key, value in values.items()}
    drift = round(1.0 - sum(normalized.values()), digits)
    if normalized:
        first_key = next(iter(normalized))
        normalized[first_key] = round(normalized[first_key] + drift, digits)
    return normalized
