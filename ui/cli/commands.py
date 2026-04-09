from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CliCommandSpec:
    name: str
    description: str


CliCommand = CliCommandSpec
