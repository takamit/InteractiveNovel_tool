from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def round_to(value: float, digits: int = 4) -> float:
    quant = Decimal("1").scaleb(-digits)
    return float(Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP))


def clamp_round(value: float, minimum: float = 0.0, maximum: float = 100.0, digits: int = 4) -> float:
    return round_to(max(minimum, min(maximum, value)), digits)
