"""
Scenario weight configurations and validation.

Each scenario has 5 explicit weights that MUST sum to 1.0.

Schedule-optimizer dimensions (all scores range [1.0, 10.0], higher = better):
  - free_days:      Days with zero classes (5 = all clear, weighted to 10)
  - compactness:    Schedule tightness, fewer gaps = higher
  - no_morning:     Morning class penalty (10.0 = no 1-2节 classes)
  - no_night:       Night class penalty (10.0 = no 11-14节 classes)
  - distribution:   Even spread across days (10.0 = balanced, no extreme skew)

Legacy dimensions (kept for API compatibility, always return 5.0 neutral):
  - gpa_score, stress_score, friday_penalty, monday_penalty, afternoon_penalty
"""

from typing import Dict

# ── Weighted coefficient table (5 dimensions × 5 scenarios) ──

SCENARIO_WEIGHTS: Dict[str, Dict[str, float]] = {
    "balanced": {
        "description": "平衡模式",
        "free_days": 0.25,
        "compactness": 0.25,
        "no_morning": 0.20,
        "no_night": 0.15,
        "distribution": 0.15,
    },
    "no_morning": {
        "description": "无早八模式",
        "free_days": 0.10,
        "compactness": 0.15,
        "no_morning": 0.60,
        "no_night": 0.10,
        "distribution": 0.05,
    },
    "compact": {
        "description": "紧凑模式",
        "free_days": 0.05,
        "compactness": 0.65,
        "no_morning": 0.15,
        "no_night": 0.10,
        "distribution": 0.05,
    },
    "leisurely": {
        "description": "休闲模式（空闲日最大化）",
        "free_days": 0.60,
        "compactness": 0.10,
        "no_morning": 0.15,
        "no_night": 0.10,
        "distribution": 0.05,
    },
    "no_night": {
        "description": "无晚课模式",
        "free_days": 0.10,
        "compactness": 0.15,
        "no_morning": 0.10,
        "no_night": 0.60,
        "distribution": 0.05,
    },
}

# ── Scenario metadata for display ──

SCENARIO_META: Dict[str, Dict[str, str]] = {
    "balanced":   {"description": "平衡模式",   "icon": "⚖️"},
    "no_morning": {"description": "无早八模式", "icon": "☀️"},
    "compact":    {"description": "紧凑模式",   "icon": "📐"},
    "leisurely":  {"description": "休闲模式",   "icon": "🏖️"},
    "no_night":   {"description": "无晚课模式", "icon": "🌙"},
}

# ── Constants ────────────────────────────────────────────────

# Current scoring dimensions
SCORING_DIMENSIONS = [
    "free_days",
    "compactness",
    "no_morning",
    "no_night",
    "distribution",
]

# Legacy dimensions (reserved for future GPA/teacher modules)
LEGACY_DIMENSIONS = [
    "gpa_score",
    "stress_score",
    "friday_penalty",
    "monday_penalty",
    "afternoon_penalty",
]

# Credit range (informational only, not a hard constraint)
MIN_CREDITS = 15
MAX_CREDITS = 25

# Stress score thresholds (legacy, kept for API compat)
STRESS_COMFORT_CREDITS = 18
STRESS_MODERATE_CREDITS = 22

# Compactness
COMPACT_FRAGMENT_DECAY = 1.5

# Period system: 1-14节, 上午=1-5, 下午=6-10, 晚上=11-14
MORNING_PERIOD_START = 1
MORNING_PERIOD_END = 5
AFTERNOON_PERIOD_START = 6
AFTERNOON_PERIOD_END = 14
EARLY_MORNING_CUTOFF = 2     # 早八 = periods 1-2
NIGHT_PERIOD_START = 11       # 晚课起点

# Penalty scores
PENALTY_NO_CLASS = 10.0
PENALTY_HAS_CLASS = 3.0
PENALTY_PER_DAY_DECAY = 1.0

# ── Validation ───────────────────────────────────────────────


def validate_scenario(scenario_id: str) -> None:
    if scenario_id not in SCENARIO_WEIGHTS:
        valid = ", ".join(sorted(SCENARIO_WEIGHTS.keys()))
        raise ValueError(f"Unknown scenario '{scenario_id}'. Valid options: {valid}")


def validate_weights(scenario_id: str) -> None:
    weights = SCENARIO_WEIGHTS[scenario_id]
    missing = [d for d in SCORING_DIMENSIONS if d not in weights]
    if missing:
        raise ValueError(f"Scenario '{scenario_id}' missing dimensions: {missing}")
    total = sum(weights[d] for d in SCORING_DIMENSIONS)
    if abs(total - 1.0) > 0.001:
        raise ValueError(f"Scenario '{scenario_id}' weights sum to {total}, expected 1.0")
