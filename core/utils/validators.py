from __future__ import annotations

from typing import Any, Iterable


def ensure(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_style_ratio_sum(style_ratio: dict[str, Any], entity_id: str, errors: list[str]) -> None:
    total = round(
        float(style_ratio.get("action", 0.0))
        + float(style_ratio.get("inner", 0.0))
        + float(style_ratio.get("cognition", 0.0))
        + float(style_ratio.get("world", 0.0)),
        4,
    )
    ensure(abs(total - 1.0) <= 0.0002, f"{entity_id}: style_ratio total must be 1.0000, got {total:.4f}", errors)


def validate_unique_ids(records: Iterable[dict[str, Any]], key: str, context: str, errors: list[str]) -> set[str]:
    seen: set[str] = set()
    for record in records:
        value = record.get(key)
        if value in seen:
            errors.append(f"{context}: duplicate {key}={value}")
        elif isinstance(value, str):
            seen.add(value)
    return seen


def validate_entity_logic(entity_data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entities = entity_data.get("entities", [])
    validate_unique_ids(entities, "id", "entities", errors)

    for entity in entities:
        entity_id = str(entity.get("id", "<unknown>"))
        style_ratio = entity.get("style_ratio", {})
        if isinstance(style_ratio, dict):
            validate_style_ratio_sum(style_ratio, entity_id, errors)

        status = entity.get("status", {})
        if isinstance(status, dict):
            loc_id = status.get("current_location_id")
            ensure(isinstance(loc_id, str) and loc_id.startswith("loc_"), f"{entity_id}: invalid current_location_id", errors)

        traits = entity.get("traits", [])
        ensure(isinstance(traits, list) and len(traits) > 0, f"{entity_id}: traits must not be empty", errors)

    return errors


def validate_relation_logic(relation_data: dict[str, Any], entity_ids: set[str]) -> list[str]:
    errors: list[str] = []
    relations = relation_data.get("relations", [])
    validate_unique_ids(relations, "id", "relations", errors)
    directional_pairs: set[tuple[str, str]] = set()

    for relation in relations:
        rel_id = str(relation.get("id", "<unknown>"))
        src = relation.get("from")
        dst = relation.get("to")
        ensure(src in entity_ids, f"{rel_id}: from references unknown entity {src}", errors)
        ensure(dst in entity_ids, f"{rel_id}: to references unknown entity {dst}", errors)
        ensure(src != dst, f"{rel_id}: self-relation is not allowed", errors)
        pair = (str(src), str(dst))
        if pair in directional_pairs:
            errors.append(f"{rel_id}: duplicate directional pair {src}->{dst}")
        directional_pairs.add(pair)

    return errors


def validate_secret_logic(secret_data: dict[str, Any], entity_ids: set[str]) -> list[str]:
    errors: list[str] = []
    secrets = secret_data.get("secrets", [])
    validate_unique_ids(secrets, "id", "secrets", errors)

    for secret in secrets:
        secret_id = str(secret.get("id", "<unknown>"))
        ks = secret.get("knowledge_states", {})
        if isinstance(ks, dict):
            for entity_id in ks.keys():
                ensure(entity_id in entity_ids, f"{secret_id}: unknown entity in knowledge_states: {entity_id}", errors)

        impact = secret.get("impact", {})
        if isinstance(impact, dict):
            for entity_id in impact.get("relation_targets", []):
                ensure(entity_id in entity_ids, f"{secret_id}: unknown relation_targets entity: {entity_id}", errors)

    return errors


def validate_location_logic(location_data: dict[str, Any], referenced_location_ids: set[str]) -> list[str]:
    errors: list[str] = []
    locations = location_data.get("locations", [])
    location_ids = validate_unique_ids(locations, "id", "locations", errors)

    for location in locations:
        loc_id = str(location.get("id", "<unknown>"))
        for connected in location.get("connected_to", []):
            ensure(connected in location_ids, f"{loc_id}: connected_to references unknown location {connected}", errors)

    for loc_id in referenced_location_ids:
        ensure(loc_id in location_ids, f"entities: referenced unknown location {loc_id}", errors)

    return errors


def collect_entity_ids(entity_data: dict[str, Any]) -> set[str]:
    return {str(entity.get("id")) for entity in entity_data.get("entities", []) if entity.get("id")}


def collect_referenced_location_ids(entity_data: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    for entity in entity_data.get("entities", []):
        status = entity.get("status", {})
        if isinstance(status, dict) and isinstance(status.get("current_location_id"), str):
            refs.add(status["current_location_id"])
    return refs
