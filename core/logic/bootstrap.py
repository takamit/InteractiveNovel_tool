from __future__ import annotations

from pathlib import Path

from core.logic.application import SimulationApplication
from core.utils.logger import configure_logging


def bootstrap_application(project_root: str | Path, *, world_name: str = "sample_world") -> SimulationApplication:
    configure_logging()
    app = SimulationApplication(project_root=project_root, world_name=world_name)
    app.bootstrap()
    return app


bootstrap = bootstrap_application
