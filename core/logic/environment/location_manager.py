from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.logic.runtime.constants import MAX_VALUE, MIN_VALUE, SOCIAL_POSITION_POWER
from core.logic.runtime.world_state import WorldState
from core.models.entities import LocationRecord


@dataclass(slots=True)
class WorldPressureProfile:
    visibility_risk: float
    hierarchy_friction: float
    institutional_weight: float
    privacy_shield: float
    pressure_score: float
    rumor_multiplier: float


class WorldPressureEngine:
    """Applies location, hierarchy, and reputation pressure as first-class constraints."""

    INSTITUTIONAL_CATEGORIES = {"institution", "classroom", "medical_corridor"}
    HIGH_VISIBILITY = {"public", "semi_public"}

    def _clamp(self, value: float) -> float:
        return round(max(MIN_VALUE, min(MAX_VALUE, value)), 4)

    def _location(self, state: WorldState, location_id: str | None) -> LocationRecord | None:
        if not location_id:
            return None
        return state.locations.get(location_id)

    def _location_anchor(self, location: LocationRecord | None) -> float:
        if location is None:
            return 0.0
        return (
            location.social_pressure * 0.42
            + location.rumor_spread_rate * 0.30
            + location.noise_level * 0.12
            - location.privacy_level * 0.18
        )

    def _power_gap(self, actor: Any, target: Any | None) -> float:
        actor_power = SOCIAL_POSITION_POWER.get(actor.status.social_position, 50.0)
        target_power = SOCIAL_POSITION_POWER.get(target.status.social_position, 50.0) if target is not None else actor_power
        return round(target_power - actor_power, 4)

    def evaluate_action_pressure(
        self,
        state: WorldState,
        actor_id: str,
        action_type: str,
        *,
        target_id: str | None = None,
        location_id: str | None = None,
    ) -> WorldPressureProfile:
        actor = state.entities[actor_id]
        target = state.entities.get(target_id) if target_id else None
        location = self._location(state, location_id or actor.status.current_location_id)
        power_gap = self._power_gap(actor, target)
        anchor = self._location_anchor(location)
        privacy = location.privacy_level if location else 0.0
        visibility = 100.0 - privacy
        social_pressure = location.social_pressure if location else 0.0
        rumor_rate = location.rumor_spread_rate if location else 0.0
        noise_level = location.noise_level if location else 0.0
        institutional = 17.0 if location and location.category in self.INSTITUTIONAL_CATEGORIES else 0.0
        if location and location.visibility not in self.HIGH_VISIBILITY:
            institutional *= 0.55

        visibility_risk = visibility * 0.42 + rumor_rate * 0.28 + max(0.0, noise_level - privacy) * 0.10
        hierarchy_friction = max(0.0, power_gap) * 0.16 + max(0.0, social_pressure - actor.status.visible_reputation) * 0.05
        privacy_shield = privacy * 0.18
        institutional_weight = institutional + (8.0 if location and location.category == "classroom" and action_type in {"confront", "confide"} else 0.0)

        action_amplifier = {
            "observe": 0.65,
            "approach": 0.82,
            "support": 0.74,
            "withdraw": 0.40,
            "confront": 1.20,
            "confide": 1.10,
            "seek_help": 0.76,
            "wait": 0.22,
        }.get(action_type, 0.75)

        raw_pressure = (visibility_risk + hierarchy_friction + institutional_weight - privacy_shield) * action_amplifier
        pressure_score = self._clamp(raw_pressure)
        rumor_multiplier = round(max(0.2, 0.55 + (visibility_risk + institutional_weight) / 110.0), 4)
        return WorldPressureProfile(
            visibility_risk=round(visibility_risk, 4),
            hierarchy_friction=round(hierarchy_friction, 4),
            institutional_weight=round(institutional_weight, 4),
            privacy_shield=round(privacy_shield, 4),
            pressure_score=round(pressure_score, 4),
            rumor_multiplier=rumor_multiplier,
        )

    def apply_action_fallout(self, state: WorldState, action: dict[str, Any]) -> list[dict[str, Any]]:
        actor = state.entities[action["actor_id"]]
        target = state.entities.get(action.get("target_id")) if action.get("target_id") else None
        location = self._location(state, action.get("location_id") or actor.status.current_location_id)
        profile = self.evaluate_action_pressure(
            state,
            actor.id,
            action["action_type"],
            target_id=action.get("target_id"),
            location_id=action.get("location_id"),
        )
        action["world_pressure"] = {
            "visibility_risk": profile.visibility_risk,
            "hierarchy_friction": profile.hierarchy_friction,
            "institutional_weight": profile.institutional_weight,
            "privacy_shield": profile.privacy_shield,
            "pressure_score": profile.pressure_score,
            "rumor_multiplier": profile.rumor_multiplier,
        }

        emitted: list[dict[str, Any]] = []
        pressure = profile.pressure_score
        action_type = action["action_type"]
        action_is_loud = action_type in {"confront", "confide", "seek_help"}
        action_is_public = location.visibility in self.HIGH_VISIBILITY if location else False
        public_heat = pressure * (1.15 if action_is_public else 0.65)

        actor.status.stress = self._clamp(actor.status.stress + pressure * 0.035)
        if target is not None and action_is_loud:
            target.status.stress = self._clamp(target.status.stress + pressure * 0.025)

        if action_is_public:
            actor.status.rumor_level = self._clamp(actor.status.rumor_level + pressure * 0.045 * profile.rumor_multiplier)
            if target is not None:
                target.status.rumor_level = self._clamp(target.status.rumor_level + pressure * 0.035 * profile.rumor_multiplier)
        elif action_type == "confide":
            actor.status.rumor_level = self._clamp(actor.status.rumor_level + max(0.0, pressure - 18.0) * 0.018)

        if target is not None and action_type == "confront" and profile.hierarchy_friction > 4.0:
            actor.status.visible_reputation = self._clamp(actor.status.visible_reputation - 0.8)
            target.status.visible_reputation = self._clamp(target.status.visible_reputation + 0.6)
            emitted.append(
                {
                    "trigger_type": "world_pressure",
                    "trigger_id": f"{actor.id}:{action_type}:hierarchy",
                    "summary": f"{actor.name.full_name} の強い行動が階層摩擦を生み、周囲の視線が厳しくなった。",
                    "affected_entities": [actor.id, target.id],
                }
            )

        if location is not None:
            location_heat = state.location_heat.get(location.id, 0.0)
            state.location_heat[location.id] = self._clamp(location_heat + public_heat * 0.20)
            state.location_pressure_history.append(
                {
                    "turn": state.turn,
                    "location_id": location.id,
                    "actor_id": actor.id,
                    "target_id": target.id if target else None,
                    "action_type": action_type,
                    "pressure_score": pressure,
                }
            )

        state.world_tension = self._clamp(state.world_tension + public_heat * 0.055)
        if pressure >= 34.0:
            emitted.append(
                {
                    "trigger_type": "world_pressure",
                    "trigger_id": f"{actor.id}:{action_type}:exposure",
                    "summary": f"{location.name if location else 'その場'} の空気が張りつめ、出来事が周囲に残りやすくなった。",
                    "affected_entities": [entity_id for entity_id in [actor.id, target.id if target else None] if entity_id],
                }
            )
        return emitted

    def apply_passive_world_drift(self, state: WorldState) -> list[dict[str, Any]]:
        emitted: list[dict[str, Any]] = []
        for location_id, heat in list(state.location_heat.items()):
            location = state.locations.get(location_id)
            if location is None:
                continue
            occupant_ids = [entity.id for entity in state.entities.values() if entity.status.current_location_id == location_id]
            if heat >= 22.0 and occupant_ids:
                for entity_id in occupant_ids:
                    entity = state.entities[entity_id]
                    entity.status.stress = self._clamp(entity.status.stress + heat * 0.018)
                    entity.status.rumor_level = self._clamp(entity.status.rumor_level + heat * 0.012)
                emitted.append(
                    {
                        "trigger_type": "world_drift",
                        "trigger_id": location_id,
                        "summary": f"{location.name} に残った空気が、そこにいる人物たちの緊張を少し押し上げた。",
                        "affected_entities": occupant_ids,
                    }
                )
            state.location_heat[location_id] = self._clamp(max(0.0, heat - (4.0 + location.privacy_level * 0.03)))

        if state.world_tension >= 28.0:
            for entity in state.entities.values():
                entity.status.rumor_level = self._clamp(entity.status.rumor_level + state.world_tension * 0.006)
            emitted.append(
                {
                    "trigger_type": "world_tension",
                    "trigger_id": "global",
                    "summary": "学園全体の空気がやや尖り、噂が自然に広まりやすくなっている。",
                    "affected_entities": list(state.entities.keys()),
                }
            )
        state.world_tension = self._clamp(max(0.0, state.world_tension - 1.8))
        return emitted
