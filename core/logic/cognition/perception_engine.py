from __future__ import annotations

from core.models.entities import CharacterEntity, LocationRecord


class PerceptionEngine:
    def perceive(self, actor: CharacterEntity, target: CharacterEntity, location: LocationRecord | None) -> dict[str, float]:
        proximity = 1.0 if actor.status.current_location_id == target.status.current_location_id else 0.0
        privacy = location.privacy_level if location else 0.0
        readability = max(0.0, target.inner_profile.maturity * 0.25 + target.emotions.affection * 0.15 - target.persona.mask_strength * 0.20 + privacy * 0.10)
        threat = max(0.0, target.emotions.anger * 0.35 + target.status.rumor_level * 0.15 + (100.0 - privacy) * 0.10)
        return {'proximity': round(proximity, 4), 'readability': round(readability, 4), 'threat': round(threat, 4)}
