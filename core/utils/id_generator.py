from __future__ import annotations


def make_turn_snapshot_name(turn: int) -> str:
    return f"turn_{turn:04d}_snapshot"
