from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.models.entities import CharacterEntity, EntityFile, LocationFile, LocationRecord, RelationFile, RelationRecord, SecretFile, SecretRecord


@dataclass(slots=True)
class WorldState:
    world_id: str
    turn: int
    entities: dict[str, CharacterEntity] = field(default_factory=dict)
    relations: dict[tuple[str, str], RelationRecord] = field(default_factory=dict)
    secrets: dict[str, SecretRecord] = field(default_factory=dict)
    locations: dict[str, LocationRecord] = field(default_factory=dict)
    event_log: list[dict[str, Any]] = field(default_factory=list)
    last_actions: list[dict[str, Any]] = field(default_factory=list)
    revealed_secrets: list[dict[str, Any]] = field(default_factory=list)
    secondary_events: list[dict[str, Any]] = field(default_factory=list)
    relation_memories: dict[str, dict[str, Any]] = field(default_factory=dict)
    secret_pressure: dict[str, float] = field(default_factory=dict)
    world_tension: float = 0.0
    location_heat: dict[str, float] = field(default_factory=dict)
    location_pressure_history: list[dict[str, Any]] = field(default_factory=list)
    save_metadata: dict[str, Any] = field(default_factory=dict)
    faction_climate: dict[str, float] = field(default_factory=dict)
    institution_pressure: float = 0.0
    reputation_pressure_log: list[dict[str, Any]] = field(default_factory=list)
    offscreen_events: list[dict[str, Any]] = field(default_factory=list)
    turn_traces: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_models(
        cls,
        entities: EntityFile,
        relations: RelationFile,
        secrets: SecretFile,
        locations: LocationFile,
        *,
        turn: int = 0,
        event_log: list[dict[str, Any]] | None = None,
        last_actions: list[dict[str, Any]] | None = None,
        revealed_secrets: list[dict[str, Any]] | None = None,
        secondary_events: list[dict[str, Any]] | None = None,
        relation_memories: dict[str, dict[str, Any]] | None = None,
        secret_pressure: dict[str, float] | None = None,
        world_tension: float | None = None,
        location_heat: dict[str, float] | None = None,
        location_pressure_history: list[dict[str, Any]] | None = None,
        save_metadata: dict[str, Any] | None = None,
        faction_climate: dict[str, float] | None = None,
        institution_pressure: float | None = None,
        reputation_pressure_log: list[dict[str, Any]] | None = None,
        offscreen_events: list[dict[str, Any]] | None = None,
        turn_traces: list[dict[str, Any]] | None = None,
    ) -> "WorldState":
        default_relation_memories: dict[str, dict[str, Any]] = {}
        if relation_memories is None:
            for relation in relations.relations:
                key = cls.make_relation_key(relation.from_, relation.to)
                default_relation_memories[key] = {
                    "touch_streak": 0.0,
                    "support_balance": 0.0,
                    "breach_count": 0,
                    "last_action": None,
                    "last_touched_turn": turn,
                    "long_term_charge": 0.0,
                }
        else:
            default_relation_memories = {key: dict(value) for key, value in relation_memories.items()}

        return cls(
            world_id=entities.world_id,
            turn=turn,
            entities={entity.id: entity.model_copy(deep=True) for entity in entities.entities},
            relations={(relation.from_, relation.to): relation.model_copy(deep=True) for relation in relations.relations},
            secrets={secret.id: secret.model_copy(deep=True) for secret in secrets.secrets},
            locations={location.id: location.model_copy(deep=True) for location in locations.locations},
            event_log=list(event_log or []),
            last_actions=list(last_actions or []),
            revealed_secrets=list(revealed_secrets or []),
            secondary_events=list(secondary_events or []),
            relation_memories=default_relation_memories,
            secret_pressure={key: float(value) for key, value in (secret_pressure or {}).items()},
            world_tension=float(world_tension or 0.0),
            location_heat={key: float(value) for key, value in (location_heat or {}).items()},
            location_pressure_history=list(location_pressure_history or []),
            save_metadata=dict(save_metadata or {}),
            faction_climate={key: float(value) for key, value in (faction_climate or {}).items()},
            institution_pressure=float(institution_pressure or 0.0),
            reputation_pressure_log=list(reputation_pressure_log or []),
            offscreen_events=list(offscreen_events or []),
            turn_traces=list(turn_traces or []),
        )

    @staticmethod
    def make_relation_key(source_id: str, target_id: str) -> str:
        return f"{source_id}->{target_id}"

    def get_relation(self, source_id: str, target_id: str) -> RelationRecord | None:
        return self.relations.get((source_id, target_id))

    def get_relation_memory(self, source_id: str, target_id: str) -> dict[str, Any]:
        key = self.make_relation_key(source_id, target_id)
        return self.relation_memories.setdefault(
            key,
            {
                "touch_streak": 0.0,
                "support_balance": 0.0,
                "breach_count": 0,
                "last_action": None,
                "last_touched_turn": self.turn,
                "long_term_charge": 0.0,
            },
        )

    def upsert_relation(self, relation: RelationRecord) -> None:
        self.relations[(relation.from_, relation.to)] = relation
        self.get_relation_memory(relation.from_, relation.to)

    def log_event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.event_log.append({"turn": self.turn, "event_type": event_type, **payload})

    def summary(self) -> dict[str, Any]:
        hot_relations = sorted(
            (
                {
                    "pair": key,
                    "charge": round(float(value.get("long_term_charge", 0.0)), 4),
                    "breach_count": int(value.get("breach_count", 0)),
                }
                for key, value in self.relation_memories.items()
            ),
            key=lambda item: (item["charge"], item["breach_count"]),
            reverse=True,
        )[:3]
        return {
            "world_id": self.world_id,
            "turn": self.turn,
            "entity_count": len(self.entities),
            "relation_count": len(self.relations),
            "secret_count": len(self.secrets),
            "revealed_secret_count": len(self.revealed_secrets),
            "secondary_event_count": len(self.secondary_events),
            "location_count": len(self.locations),
            "last_actions": list(self.last_actions),
            "event_log_size": len(self.event_log),
            "hot_relations": hot_relations,
            "secret_pressure": {key: round(value, 4) for key, value in self.secret_pressure.items()},
            "world_tension": round(self.world_tension, 4),
            "location_heat": {key: round(value, 4) for key, value in self.location_heat.items()},
            "location_pressure_events": len(self.location_pressure_history),
            "save_metadata": dict(self.save_metadata),
            "faction_climate": {key: round(value, 4) for key, value in self.faction_climate.items()},
            "institution_pressure": round(self.institution_pressure, 4),
            "reputation_pressure_events": len(self.reputation_pressure_log),
            "offscreen_event_count": len(self.offscreen_events),
            "turn_trace_count": len(self.turn_traces),
        }
