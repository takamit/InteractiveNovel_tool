from __future__ import annotations

INTERNAL_PRECISION = 4
DISPLAY_PRECISION = 1
MAX_VALUE = 100.0
MIN_VALUE = 0.0
SNAPSHOT_VERSION = 5

NEED_PRIORITY_WEIGHTS = {
    "hunger": 1.00,
    "thirst": 1.05,
    "sleepiness": 0.90,
    "health": 1.10,
    "sexual_desire": 0.40,
    "intimacy": 0.75,
    "belonging": 0.85,
    "approval": 0.60,
    "safety": 1.00,
    "power": 0.65,
    "freedom": 0.70,
}

EMOTION_DECAY_PER_TURN = {
    "joy": 1.2,
    "anger": 1.6,
    "sadness": 1.0,
    "fear": 1.3,
    "affection": 0.6,
}

DEFAULT_NEED_DRIFT = {
    "hunger": 2.0,
    "thirst": 2.4,
    "sleepiness": 1.5,
    "health": -0.2,
    "sexual_desire": 0.7,
    "intimacy": 1.0,
    "belonging": 0.9,
    "approval": 0.6,
    "safety": 0.2,
    "power": 0.4,
    "freedom": 0.5,
}

RELATION_ACTION_EFFECTS = {
    "approach": {"like": 1.1, "trust": 0.8, "interest": 0.9, "maintenance": 0.5},
    "observe": {"interest": 0.5, "maintenance": 0.2},
    "support": {"trust": 1.6, "like": 1.0, "intimacy": 0.7, "maintenance": 0.8},
    "confront": {"suspicion": 1.2, "fear": 0.7, "respect": 0.5, "resentment": 0.9, "maintenance": -0.3},
    "withdraw": {"suspicion": 0.3, "maintenance": -0.8, "decay": 0.5},
    "confide": {"trust": 1.9, "intimacy": 1.6, "attachment": 1.1, "maintenance": 0.9},
    "seek_help": {"trust": 1.1, "dependence": 1.4, "intimacy": 0.5, "maintenance": 0.7},
    "wait": {"decay": 0.2},
}

TARGET_REACTION_EFFECTS = {
    "approach": {"like": 0.5, "interest": 0.6},
    "observe": {"interest": 0.2},
    "support": {"trust": 0.9, "like": 0.5, "respect": 0.3},
    "confront": {"suspicion": 1.0, "fear": 0.5, "resentment": 1.1},
    "withdraw": {"suspicion": 0.2, "attachment": -0.2},
    "confide": {"trust": 1.2, "intimacy": 1.0, "attachment": 0.7},
    "seek_help": {"trust": 0.8, "dependence": 0.9, "respect": 0.2},
    "wait": {},
}

SECRET_VISIBILITY_ORDER = ["hidden", "implied", "rumored", "revealed"]
SECRET_KNOWLEDGE_ORDER = ["unknown", "misunderstood", "rumored", "partially_known", "known"]

ACTION_ENGINE_AFFINITY = {
    "observe": {"action": 0.10, "inner": 0.15, "cognition": 1.00, "world": 0.55},
    "approach": {"action": 0.55, "inner": 0.85, "cognition": 0.35, "world": 0.30},
    "support": {"action": 0.45, "inner": 0.95, "cognition": 0.45, "world": 0.20},
    "withdraw": {"action": 0.25, "inner": 0.60, "cognition": 0.55, "world": 0.65},
    "confront": {"action": 1.00, "inner": 0.45, "cognition": 0.30, "world": 0.40},
    "confide": {"action": 0.20, "inner": 1.00, "cognition": 0.55, "world": 0.15},
    "seek_help": {"action": 0.25, "inner": 0.85, "cognition": 0.40, "world": 0.35},
    "wait": {"action": 0.05, "inner": 0.10, "cognition": 0.40, "world": 0.75},
}

ACTION_IDEOLOGY_BIAS = {
    "observe": {"understanding", "truth_pattern", "predictability"},
    "approach": {"belonging", "social_balance", "smooth_interaction"},
    "support": {"fairness", "noninterference_until_needed", "dignity"},
    "withdraw": {"self_preservation", "safety", "freedom"},
    "confront": {"strength", "status", "control"},
    "confide": {"controlled_honesty", "emotional_anchor", "honesty"},
    "seek_help": {"self_preservation", "not_being_left_behind"},
    "wait": {"predictability", "control"},
}

SOCIAL_POSITION_POWER = {
    "lower": 25.0,
    "middle_low": 38.0,
    "middle": 50.0,
    "unstable_middle": 48.0,
    "upper_middle": 68.0,
    "upper": 80.0,
}
