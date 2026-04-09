from __future__ import annotations

from typing import Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Name(StrictBaseModel):
    family_name: str
    given_name: str
    full_name: str
    reading: str


class Role(StrictBaseModel):
    primary: str
    secondary: str
    archetype: str


class Demographics(StrictBaseModel):
    age: int = Field(ge=0)
    school_year: int = Field(ge=1)
    class_name: str
    gender: str


class AxisRatio(StrictBaseModel):
    action: float = Field(ge=0.0, le=1.0)
    inner: float = Field(ge=0.0, le=1.0)
    cognition: float = Field(ge=0.0, le=1.0)
    world: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_total(self) -> "AxisRatio":
        total = round(self.action + self.inner + self.cognition + self.world, 4)
        if abs(total - 1.0) > 0.0002:
            raise ValueError(f"style_ratio total must be 1.0000, got {total:.4f}")
        return self


class AxisIntensity100(StrictBaseModel):
    action: float = Field(ge=0.0, le=100.0)
    inner: float = Field(ge=0.0, le=100.0)
    cognition: float = Field(ge=0.0, le=100.0)
    world: float = Field(ge=0.0, le=100.0)


class ContextModifierEntry(StrictBaseModel):
    action: float = Field(ge=-100.0, le=100.0)
    inner: float = Field(ge=-100.0, le=100.0)
    cognition: float = Field(ge=-100.0, le=100.0)
    world: float = Field(ge=-100.0, le=100.0)



class Ideology(StrictBaseModel):
    core_values: List[str]
    taboo_values: List[str]
    belief_style: str


class RelationTendency(StrictBaseModel):
    attachment_speed: float = Field(ge=0.0, le=100.0)
    trust_growth_rate: float = Field(ge=0.0, le=100.0)
    suspicion_growth_rate: float = Field(ge=0.0, le=100.0)
    maintenance_need: float = Field(ge=0.0, le=100.0)
    jealousy_bias: float = Field(ge=0.0, le=100.0)
    forgiveness_rate: float = Field(ge=0.0, le=100.0)
    asymmetry_tolerance: float = Field(ge=0.0, le=100.0)


class InnerProfile(StrictBaseModel):
    self_evaluation: float = Field(ge=0.0, le=100.0)
    insecurity: float = Field(ge=0.0, le=100.0)
    maturity: float = Field(ge=0.0, le=100.0)
    pride: float = Field(ge=0.0, le=100.0)
    loneliness: float = Field(ge=0.0, le=100.0)


class SurvivalNeeds(StrictBaseModel):
    hunger: float = Field(ge=0.0, le=100.0)
    thirst: float = Field(ge=0.0, le=100.0)
    sleepiness: float = Field(ge=0.0, le=100.0)
    health: float = Field(ge=0.0, le=100.0)


class ReproductionNeeds(StrictBaseModel):
    sexual_desire: float = Field(ge=0.0, le=100.0)
    intimacy: float = Field(ge=0.0, le=100.0)


class PsychologicalNeeds(StrictBaseModel):
    belonging: float = Field(ge=0.0, le=100.0)
    approval: float = Field(ge=0.0, le=100.0)
    safety: float = Field(ge=0.0, le=100.0)
    power: float = Field(ge=0.0, le=100.0)
    freedom: float = Field(ge=0.0, le=100.0)


class Needs(StrictBaseModel):
    survival: SurvivalNeeds
    reproduction: ReproductionNeeds
    psychological: PsychologicalNeeds


class Emotions(StrictBaseModel):
    joy: float = Field(ge=0.0, le=100.0)
    anger: float = Field(ge=0.0, le=100.0)
    sadness: float = Field(ge=0.0, le=100.0)
    fear: float = Field(ge=0.0, le=100.0)
    affection: float = Field(ge=0.0, le=100.0)


class Persona(StrictBaseModel):
    surface_persona: str
    hidden_persona: str
    mask_strength: float = Field(ge=0.0, le=100.0)
    switch_threshold: float = Field(ge=0.0, le=100.0)


class Status(StrictBaseModel):
    current_location_id: str
    social_position: str
    visible_reputation: float = Field(ge=0.0, le=100.0)
    hidden_reputation: float = Field(ge=0.0, le=100.0)
    rumor_level: float = Field(ge=0.0, le=100.0)
    fatigue: float = Field(ge=0.0, le=100.0)
    stress: float = Field(ge=0.0, le=100.0)
    injury: float = Field(ge=0.0, le=100.0)
    financial_level: float = Field(ge=0.0, le=100.0)


class CharacterFlags(StrictBaseModel):
    is_npc: bool
    is_promotable: bool
    is_viewpoint_candidate: bool
    is_hidden_key_actor: bool


class CharacterEntity(StrictBaseModel):
    id: str
    type: Literal["character"]
    name: Name
    role: Role
    demographics: Demographics
    style_ratio: AxisRatio
    intensity: AxisIntensity100
    context_modifier: Dict[str, ContextModifierEntry] = Field(default_factory=dict)
    ideology: Ideology
    relation_tendency: RelationTendency
    inner_profile: InnerProfile
    needs: Needs
    emotions: Emotions
    persona: Persona
    status: Status
    traits: List[str]
    flags: CharacterFlags

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not value.startswith("char_"):
            raise ValueError("character id must start with char_")
        return value


class EntityFile(StrictBaseModel):
    world_id: str
    entities: List[CharacterEntity]


class RelationBasic(StrictBaseModel):
    like: float = Field(ge=0.0, le=100.0)
    trust: float = Field(ge=0.0, le=100.0)
    respect: float = Field(ge=0.0, le=100.0)
    fear: float = Field(ge=0.0, le=100.0)
    suspicion: float = Field(ge=0.0, le=100.0)


class RelationExtended(StrictBaseModel):
    interest: float = Field(ge=0.0, le=100.0)
    dependence: float = Field(ge=0.0, le=100.0)
    attachment: float = Field(ge=0.0, le=100.0)
    attraction: float = Field(ge=0.0, le=100.0)
    intimacy: float = Field(ge=0.0, le=100.0)


class RelationAdvanced(StrictBaseModel):
    desire: float = Field(ge=0.0, le=100.0)
    exclusivity: float = Field(ge=0.0, le=100.0)
    obsession: float = Field(ge=0.0, le=100.0)
    control: float = Field(ge=0.0, le=100.0)
    devotion: float = Field(ge=0.0, le=100.0)
    resentment: float = Field(ge=0.0, le=100.0)


class RelationLabels(StrictBaseModel):
    structural: List[str]
    emotional: List[str]
    perception: List[str]


class RelationRecord(StrictBaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    from_: str = Field(alias="from")
    to: str
    basic: RelationBasic
    extended: RelationExtended
    advanced: RelationAdvanced
    labels: RelationLabels
    maintenance: float = Field(ge=0.0, le=100.0)
    decay: float = Field(ge=0.0, le=100.0)
    asymmetry: float = Field(ge=0.0, le=100.0)
    trend: str


class RelationFile(StrictBaseModel):
    world_id: str
    relations: List[RelationRecord]


KnowledgeState = Literal["known", "partially_known", "rumored", "misunderstood", "unknown"]
SecretVisibility = Literal["hidden", "implied", "rumored", "revealed"]
LocationVisibility = Literal["public", "semi_public", "restricted", "semi_restricted"]


class SecretImpact(StrictBaseModel):
    relation_targets: List[str]
    emotion_effects: List[str]
    world_effects: List[str]


class SecretRecord(StrictBaseModel):
    id: str
    title: str
    category: str
    objective_truth: str
    visibility: SecretVisibility
    knowledge_states: Dict[str, KnowledgeState]
    reveal_conditions: List[str]
    impact: SecretImpact
    priority: float = Field(ge=0.0, le=100.0)


class SecretFile(StrictBaseModel):
    world_id: str
    secrets: List[SecretRecord]


class LocationRecord(StrictBaseModel):
    id: str
    name: str
    category: str
    visibility: LocationVisibility
    noise_level: float = Field(ge=0.0, le=100.0)
    privacy_level: float = Field(ge=0.0, le=100.0)
    social_pressure: float = Field(ge=0.0, le=100.0)
    rumor_spread_rate: float = Field(ge=0.0, le=100.0)
    emotional_tags: List[str]
    connected_to: List[str]
    description: str


class LocationFile(StrictBaseModel):
    world_id: str
    locations: List[LocationRecord]
