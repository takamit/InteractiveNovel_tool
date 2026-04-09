from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any

from core.logic.runtime.world_state import WorldState


@dataclass(slots=True)
class ReleaseDiagnostics:
    """Evaluate world balance and release readiness from a world snapshot."""

    stress_warn: float = 78.0
    stress_critical: float = 90.0
    tension_warn: float = 72.0
    tension_critical: float = 88.0
    suspicion_warn: float = 82.0
    heat_warn: float = 82.0

    def build_report(self, state: WorldState) -> dict[str, Any]:
        entity_rows = [
            {
                "entity_id": entity.id,
                "name": entity.name.full_name,
                "stress": round(entity.status.stress, 4),
                "rumor_level": round(entity.status.rumor_level, 4),
                "fatigue": round(entity.status.fatigue, 4),
            }
            for entity in state.entities.values()
        ]
        relation_rows = [
            {
                "pair": f"{relation.from_}->{relation.to}",
                "trust": round(relation.basic.trust, 4),
                "suspicion": round(relation.basic.suspicion, 4),
                "trend": relation.trend,
            }
            for relation in state.relations.values()
        ]
        warnings: list[str] = []
        blockers: list[str] = []

        max_stress = max((row["stress"] for row in entity_rows), default=0.0)
        avg_stress = mean([row["stress"] for row in entity_rows]) if entity_rows else 0.0
        max_heat = max(state.location_heat.values(), default=0.0)
        max_suspicion = max((row["suspicion"] for row in relation_rows), default=0.0)
        avg_suspicion = mean([row["suspicion"] for row in relation_rows]) if relation_rows else 0.0

        if max_stress >= self.stress_critical:
            blockers.append(f"stress critical: {max_stress:.1f}")
        elif max_stress >= self.stress_warn:
            warnings.append(f"stress high: {max_stress:.1f}")

        if state.world_tension >= self.tension_critical:
            blockers.append(f"world tension critical: {state.world_tension:.1f}")
        elif state.world_tension >= self.tension_warn:
            warnings.append(f"world tension high: {state.world_tension:.1f}")

        if max_suspicion >= self.suspicion_warn:
            warnings.append(f"suspicion spike: {max_suspicion:.1f}")

        if max_heat >= self.heat_warn:
            warnings.append(f"location heat spike: {max_heat:.1f}")

        if len(state.revealed_secrets) == 0 and state.turn >= 10:
            warnings.append("no secrets have surfaced after 10 turns")

        if len(state.last_actions) == 0:
            blockers.append("no actions recorded")

        score = 100.0
        score -= len(warnings) * 6.0
        score -= len(blockers) * 15.0
        score -= min(avg_stress / 10.0, 10.0)
        score -= min(avg_suspicion / 14.0, 7.0)
        score = round(max(0.0, min(100.0, score)), 2)

        highest_stress = sorted(entity_rows, key=lambda item: item["stress"], reverse=True)[:5]
        hottest_locations = sorted(
            ({"location_id": key, "heat": round(value, 4)} for key, value in state.location_heat.items()),
            key=lambda item: item["heat"],
            reverse=True,
        )[:5]

        return {
            "turn": state.turn,
            "release_score": score,
            "release_ready": not blockers,
            "warnings": warnings,
            "blockers": blockers,
            "metrics": {
                "entity_count": len(state.entities),
                "relation_count": len(state.relations),
                "revealed_secret_count": len(state.revealed_secrets),
                "offscreen_event_count": len(state.offscreen_events),
                "world_tension": round(state.world_tension, 4),
                "avg_stress": round(avg_stress, 4),
                "max_stress": round(max_stress, 4),
                "avg_suspicion": round(avg_suspicion, 4),
                "max_suspicion": round(max_suspicion, 4),
                "max_location_heat": round(max_heat, 4),
            },
            "highest_stress": highest_stress,
            "hottest_locations": hottest_locations,
            "recent_offscreen_events": list(state.offscreen_events[-5:]),
            "summary": state.summary(),
        }
