from __future__ import annotations

from pathlib import Path
from typing import Any

from core.logic.runtime.engine import SimulationEngine
from ui.components.play.choice_presenter import PlayerChoicePresenter
from core.utils.logger import configure_logging, get_logger


class SimulationApplication:
    """High-level application facade for simulation, analysis, and player-driven turns."""

    def __init__(self, project_root: str | Path, *, world_name: str = "sample_world") -> None:
        self.project_root = Path(project_root)
        self.engine = SimulationEngine(project_root=self.project_root, world_name=world_name)
        self.logger = get_logger(__name__)
        self.choice_presenter = PlayerChoicePresenter()

    def bootstrap(self) -> None:
        self.engine.bootstrap()
        self.logger.info("Application bootstrapped for world=%s", self.engine.world_name)

    def run_turns(self, turns: int = 1, *, autosave: bool = False) -> list[dict[str, Any]]:
        if turns <= 0:
            raise ValueError("turns must be >= 1")
        results: list[dict[str, Any]] = []
        for _ in range(turns):
            result = self.engine.run_turn(autosave=autosave)
            results.append({
                "turn": result.turn,
                "highlights": list(result.highlights),
                "action_count": len(result.actions),
                "secret_event_count": len(result.secret_events),
                "secondary_event_count": len(result.secondary_events),
            })
        return results

    def list_player_options(self, player_entity_id: str, *, target_id: str | None = None) -> list[dict[str, Any]]:
        return self.engine.list_player_options(player_entity_id=player_entity_id, target_id=target_id)

    def list_presented_player_options(self, player_entity_id: str, *, target_id: str | None = None) -> list[dict[str, Any]]:
        state = self.engine._ensure_state()
        options = self.engine.list_player_options(player_entity_id=player_entity_id, target_id=target_id)
        return self.choice_presenter.present_options(state, player_entity_id, options)

    def list_target_options(self, player_entity_id: str) -> list[dict[str, str]]:
        return self.engine.list_target_options(player_entity_id=player_entity_id)

    def run_player_turn(
        self,
        *,
        player_entity_id: str,
        action_type: str,
        target_id: str | None = None,
        autosave: bool = False,
    ) -> dict[str, Any]:
        result = self.engine.run_player_turn(
            player_entity_id=player_entity_id,
            action_type=action_type,
            target_id=target_id,
            autosave=autosave,
        )
        return {
            "turn": result.turn,
            "highlights": list(result.highlights),
            "action_count": len(result.actions),
            "secret_event_count": len(result.secret_events),
            "secondary_event_count": len(result.secondary_events),
        }

    def render(self, *, mode: str = "omniscient", focal_entity_id: str | None = None) -> str:
        return self.engine.render_latest_turn(mode=mode, focal_entity_id=focal_entity_id)

    def analysis(self) -> dict[str, Any]:
        return self.engine.analysis_report()

    def snapshot(self) -> dict[str, Any]:
        return self.engine.snapshot()

    def save(self, *, slot_name: str = "slot_01") -> Path:
        return self.engine.save(slot_name=slot_name)

    def release_report(self) -> dict[str, Any]:
        return self.engine.release_report()

    def endurance_report(self, snapshots: list[dict[str, Any]]) -> dict[str, Any]:
        return self.engine.endurance_report(snapshots)


DialogueNovelApp = SimulationApplication


def create_app(project_root: str | Path, *, world_name: str = "sample_world") -> SimulationApplication:
    configure_logging()
    app = SimulationApplication(project_root, world_name=world_name)
    app.bootstrap()
    return app
