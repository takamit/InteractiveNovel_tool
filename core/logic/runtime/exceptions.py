from __future__ import annotations


class SimulationError(Exception):
    """Base exception for the simulation project."""


class WorldDataLoadError(SimulationError):
    """Raised when world JSON or schema validation fails."""
