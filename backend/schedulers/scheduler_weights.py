"""
Scheduler weights — scenario-specific penalties for Phase 2 optimization.

Coverage is maximized in Phase 1 (always pick max feasible courses).
These weights only affect WHICH courses are chosen within max-coverage sets.

early  = penalty per course starting at period <= 2 (higher = fewer mornings)
night  = penalty per course starting at period >= 11 (higher = fewer nights)
friday = bonus for having Friday completely free
"""

DEFAULT_WEIGHTS = {
    "early": 100,
    "night": 100,
    "friday": 100,
    "day_spread": 300,  # penalty per day with classes (pushes compression)
}

SCENARIO_WEIGHTS = {
    "balanced": {
        "early": 100, "night": 100, "friday": 100, "day_spread": 300,
    },
    "no_morning": {
        "early": 500, "night": 100, "friday": 80, "day_spread": 200,
    },
    "compact": {
        "early": 150, "night": 100, "friday": 150, "day_spread": 600,
    },
    "leisurely": {
        "early": 100, "night": 100, "friday": 500, "day_spread": 400,
    },
    "no_night": {
        "early": 100, "night": 500, "friday": 80, "day_spread": 200,
    },
}


def get_weights(scenario: str) -> dict[str, int]:
    return SCENARIO_WEIGHTS.get(scenario, DEFAULT_WEIGHTS)
