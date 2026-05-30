"""
Scenario weight configurations and validation.

Each scenario has 8 explicit weights that MUST sum to 1.0.
The engine accesses weights directly (not via .get()) so any missing
key will fail loudly at development time rather than silently producing
incorrect scores.

Weight dimensions (all scores range [1.0, 10.0], higher is better):
  - gpa_score:          Teacher rating average × 2
  - compact_score:      Schedule compactness (continuous decay)
  - stress_score:       Credit load pressure (lower credits = higher score)
  - free_score:         Number of completely free half-days
  - morning_penalty:    Penalty for morning classes (10.0 = no mornings)
  - friday_penalty:     Penalty for Friday classes (10.0 = free Friday)
  - monday_penalty:     Penalty for Monday classes (10.0 = free Monday)
  - afternoon_penalty:  Penalty for afternoon/evening classes
"""

from typing import Dict

# ── Weighted coefficient table (8 dimensions × 5 scenarios) ──
# Each scenario's 8 weights sum to exactly 1.0.

SCENARIO_WEIGHTS: Dict[str, Dict[str, float]] = {
    "no_morning": {
        "description": "无早八模式",
        "gpa_score": 0.25,
        "compact_score": 0.25,
        "stress_score": 0.15,
        "free_score": 0.15,
        "morning_penalty": 0.15,
        "friday_penalty": 0.05,
        "monday_penalty": 0.00,
        "afternoon_penalty": 0.00,
    },
    "long_weekend": {
        "description": "三天小长假（周一或周五尽量空出）",
        "gpa_score": 0.15,
        "compact_score": 0.15,
        "stress_score": 0.15,
        "free_score": 0.20,
        "morning_penalty": 0.05,
        "friday_penalty": 0.15,
        "monday_penalty": 0.15,
        "afternoon_penalty": 0.00,
    },
    "morning_only": {
        "description": "上午集中型",
        "gpa_score": 0.20,
        "compact_score": 0.30,
        "stress_score": 0.10,
        "free_score": 0.15,
        "morning_penalty": 0.05,
        "friday_penalty": 0.00,
        "monday_penalty": 0.00,
        "afternoon_penalty": 0.20,
    },
    "balanced": {
        "description": "紧凑课表（最大化完整空闲块）",
        "gpa_score": 0.20,
        "compact_score": 0.25,
        "stress_score": 0.10,
        "free_score": 0.25,
        "morning_penalty": 0.05,
        "friday_penalty": 0.10,
        "monday_penalty": 0.05,
        "afternoon_penalty": 0.00,
    },
    "easy_mode": {
        "description": "轻松过渡期",
        "gpa_score": 0.15,
        "compact_score": 0.15,
        "stress_score": 0.45,
        "free_score": 0.10,
        "morning_penalty": 0.10,
        "friday_penalty": 0.05,
        "monday_penalty": 0.00,
        "afternoon_penalty": 0.00,
    },
    "gpa_focus": {
        "description": "GPA狂飙",
        "gpa_score": 0.70,
        "compact_score": 0.05,
        "stress_score": 0.10,
        "free_score": 0.05,
        "morning_penalty": 0.05,
        "friday_penalty": 0.05,
        "monday_penalty": 0.00,
        "afternoon_penalty": 0.00,
    },
}

# ── Scenario metadata for display and validation messages ──

SCENARIO_META: Dict[str, Dict[str, str]] = {
    "no_morning": {
        "description": "无早八模式",
        "icon": "🛌",
    },
    "long_weekend": {
        "description": "三天小长假",
        "icon": "📅",
    },
    "morning_only": {
        "description": "上午集中型",
        "icon": "🏋️",
    },
    "balanced": {
        "description": "紧凑课表",
        "icon": "📐",
    },
    "easy_mode": {
        "description": "轻松过渡期",
        "icon": "😌",
    },
    "gpa_focus": {
        "description": "GPA狂飙",
        "icon": "🎯",
    },
}

# ── Constants ────────────────────────────────────────────────

# Scoring dimension keys (used to validate weight dictionaries)
SCORING_DIMENSIONS = [
    "gpa_score",
    "compact_score",
    "stress_score",
    "free_score",
    "morning_penalty",
    "friday_penalty",
    "monday_penalty",
    "afternoon_penalty",
]

# Credit range hard constraint
MIN_CREDITS = 15
MAX_CREDITS = 25

# Stress score thresholds
STRESS_COMFORT_CREDITS = 18  # <= this → score = 10.0
STRESS_MODERATE_CREDITS = 22  # 18-22 → linear decay

# Compactness scoring
COMPACT_FRAGMENT_DECAY = 1.5  # per-fragment decay rate

# Penalty scoring
# Period system: 1-14节, 上午=1-5, 下午=6-10, 晚上=11-14
MORNING_PERIOD_START = 1   # morning starts at period 1
MORNING_PERIOD_END = 5     # morning ends at period 5
AFTERNOON_PERIOD_START = 6  # afternoon starts at period 6
AFTERNOON_PERIOD_END = 14   # afternoon+evening ends at period 14
EARLY_MORNING_CUTOFF = 2    # 早八 = periods 1-2 (the earliest time slot)

# Day-specific penalty scores
PENALTY_NO_CLASS = 10.0  # perfect score when no class on that day
PENALTY_HAS_CLASS = 3.0  # penalty when class exists on that day
PENALTY_PER_DAY_DECAY = 1.0  # per-day decay for continuous penalties

# ── Validation ───────────────────────────────────────────────


def validate_scenario(scenario_id: str) -> None:
    """Validate that a scenario ID is known.

    Args:
        scenario_id: The scenario identifier to check.

    Raises:
        ValueError: If the scenario is not in SCENARIO_WEIGHTS,
            with a message listing all valid options.
    """
    if scenario_id not in SCENARIO_WEIGHTS:
        valid = ", ".join(sorted(SCENARIO_WEIGHTS.keys()))
        raise ValueError(
            f"Unknown scenario '{scenario_id}'. Valid options: {valid}"
        )


def validate_weights(scenario_id: str) -> None:
    """Validate that a scenario's weights sum to 1.0.

    This is a development-time sanity check, not called at runtime.
    Use it in tests to catch weight configuration errors.

    Args:
        scenario_id: The scenario to validate.

    Raises:
        ValueError: If weights don't sum to 1.0 or if dimensions are missing.
    """
    weights = SCENARIO_WEIGHTS[scenario_id]
    missing = [d for d in SCORING_DIMENSIONS if d not in weights]
    if missing:
        raise ValueError(
            f"Scenario '{scenario_id}' missing dimensions: {missing}"
        )

    total = sum(weights[d] for d in SCORING_DIMENSIONS)
    if abs(total - 1.0) > 0.001:
        raise ValueError(
            f"Scenario '{scenario_id}' weights sum to {total}, expected 1.0"
        )
