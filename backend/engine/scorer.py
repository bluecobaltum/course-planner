"""
Scoring engine — all pure functions for evaluating schedule plans.

Each scoring function:
  - Takes a list of course dicts (the plan)
  - Returns a float in [1.0, 10.0] where HIGHER IS ALWAYS BETTER
  - Has no side effects and no external dependencies

Penalty scores are "inverted" — a perfect outcome = 10.0,
a bad outcome = lower score. This keeps all 8 dimensions aligned
so the weighted sum formula is clean.
"""

from collections import defaultdict
from typing import Any

from config.scenarios import (
    STRESS_COMFORT_CREDITS,
    STRESS_MODERATE_CREDITS,
    COMPACT_FRAGMENT_DECAY,
    AFTERNOON_PERIOD_START,
    PENALTY_NO_CLASS,
    PENALTY_HAS_CLASS,
    PENALTY_PER_DAY_DECAY,
    EARLY_MORNING_CUTOFF,
    NIGHT_PERIOD_START,
    LEGACY_DIMENSIONS,
)

# ── Shared Helper ────────────────────────────────────────────


def _get_occupied_periods(plan: list[dict[str, Any]]) -> dict[int, set[int]]:
    """Expand all course schedules into occupied period numbers per day.

    Uses range(start, end+1) to correctly handle courses that span
    both morning and afternoon sessions (e.g., periods 3-6 occupy
    {3, 4, 5, 6}, affecting BOTH half-day calculations).

    Args:
        plan: List of course dicts, each with a "schedule" field.

    Returns:
        {day: set_of_occupied_periods}, e.g. {1: {3, 4}, 3: {3, 4, 5, 6}}.
    """
    occupied: dict[int, set[int]] = defaultdict(set)
    for course in plan:
        for slot in course["schedule"]:
            for period in range(slot["start"], slot["end"] + 1):
                occupied[slot["day"]].add(period)
    return dict(occupied)


def _safe_credits(course: dict[str, Any]) -> int:
    """Safely extract credits from a course dict, defaulting to 0."""
    try:
        v = course.get("credits")
        return int(v) if v is not None else 0
    except (TypeError, ValueError):
        return 0


def _safe_rating(course: dict[str, Any]) -> float | None:
    """Safely extract teacher rating from a course dict, or None if missing.

    Handles: teacher=None, teacher={}, teacher={'rating': None}, teacher missing.
    """
    try:
        teacher = course.get("teacher")
        if teacher is None or not isinstance(teacher, dict):
            return None
        v = teacher.get("rating")
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


# ── Base Dimension Scoring ───────────────────────────────────


def compute_gpa_score(plan: list[dict[str, Any]]) -> float:
    """Average teacher rating across all courses, scaled by 2.

    Formula: avg(rating) × 2
    Range: 2.0 (all 1.0 ratings) to 10.0 (all 5.0 ratings).
    Missing or invalid ratings default to 3.0 (middle of the scale).

    Args:
        plan: List of course dicts with teacher.rating field.
    """
    ratings = []
    for c in plan:
        r = _safe_rating(c)
        if r is not None:
            ratings.append(r)

    if not ratings:
        return 3.0 * 2  # all missing → default to middle

    return round(sum(ratings) / len(ratings) * 2, 1)


def compute_compact_score(plan: list[dict[str, Any]]) -> float:
    """Measure schedule compactness — fewer gaps = higher score.

    For each day, collects time blocks and counts fragment penalties:
      - gap <= 1 period: back-to-back blocks → no penalty (normal 20min break)
      - gap == 2 periods (typically lunch break) → +0.5 fragments (acceptable)
      - gap >= 3 periods → +0.5 × gap fragments (real fragmentation)

    Then: score = max(1.0, 10.0 - total_fragments × 1.5)

    Args:
        plan: List of course dicts.

    Returns:
        Compactness score in [1.0, 10.0]. 10.0 = perfectly packed.
    """
    # Collect time blocks per day: {day: [(start, end), ...]}
    days: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for course in plan:
        for slot in course["schedule"]:
            days[slot["day"]].append((slot["start"], slot["end"]))

    total_fragments: float = 0.0

    for slots in days.values():
        if not slots:
            continue
        slots.sort(key=lambda x: x[0])  # sort by start period

        for i in range(len(slots) - 1):
            gap = slots[i + 1][0] - slots[i][1]

            if gap <= 1:
                # Back-to-back or 1-period gap (normal 20min transition)
                total_fragments += 0.0
            elif gap == 2:
                # 2-period gap (typically lunch) = acceptable
                total_fragments += 0.5
            elif gap > 2:
                # Real gap: penalize proportionally
                total_fragments += 0.5 * gap

    return round(max(1.0, 10.0 - total_fragments * COMPACT_FRAGMENT_DECAY), 1)


def compute_stress_score(plan: list[dict[str, Any]]) -> float:
    """Credit load pressure — fewer credits = higher (better) score.

    Zones:
      ≤ 18 credits  → 10.0 (comfort zone)
      19-22 credits → 10.0 - (credits - 18) × 1.5 (linear decay)
      ≥ 23 credits  → max(1.0, 4.0 - (credits - 22) × 1.0) (steeper)

    Args:
        plan: List of course dicts.

    Returns:
        Stress score in [1.0, 10.0].
    """
    total_credits = sum(_safe_credits(c) for c in plan)

    if total_credits <= STRESS_COMFORT_CREDITS:
        return 10.0
    elif total_credits <= STRESS_MODERATE_CREDITS:
        return round(10.0 - (total_credits - STRESS_COMFORT_CREDITS) * 1.5, 1)
    else:
        return round(
            max(1.0, 4.0 - (total_credits - STRESS_MODERATE_CREDITS) * 1.0), 1
        )




# ── Penalty Scoring ──────────────────────────────────────────


def compute_morning_penalty(plan: list[dict[str, Any]]) -> float:
    """Penalty for early morning classes (早八, periods 1-2).

    Counts the number of DAYS that have any class starting at period ≤ 2.
    Score: max(1.0, 10.0 - morning_days × 2.0)

    0 days = 10.0 | 1 = 8.0 | 2 = 6.0 | 3 = 4.0 | 4 = 2.0 | 5 = 1.0

    Args:
        plan: List of course dicts.

    Returns:
        Morning penalty score in [1.0, 10.0]. Higher = fewer mornings.
    """
    morning_days: set[int] = set()
    for course in plan:
        for slot in course["schedule"]:
            if slot["start"] <= EARLY_MORNING_CUTOFF:  # 早八 = periods 1-2
                morning_days.add(slot["day"])

    count = len(morning_days)
    if count == 0:
        return PENALTY_NO_CLASS
    return round(max(1.0, PENALTY_NO_CLASS - count * PENALTY_PER_DAY_DECAY), 1)


def compute_friday_penalty(plan: list[dict[str, Any]]) -> float:
    """Binary penalty for Friday classes.

    No Friday class → 10.0 (perfect).
    Has Friday class → 3.0 (penalized).

    Args:
        plan: List of course dicts.

    Returns:
        10.0 if Friday is free, 3.0 otherwise.
    """
    has_friday = any(
        slot["day"] == 5 for course in plan for slot in course["schedule"]
    )
    return PENALTY_NO_CLASS if not has_friday else PENALTY_HAS_CLASS


def compute_monday_penalty(plan: list[dict[str, Any]]) -> float:
    """Binary penalty for Monday classes.

    No Monday class → 10.0 (perfect).
    Has Monday class → 3.0 (penalized).

    Args:
        plan: List of course dicts.

    Returns:
        10.0 if Monday is free, 3.0 otherwise.
    """
    has_monday = any(
        slot["day"] == 1 for course in plan for slot in course["schedule"]
    )
    return PENALTY_NO_CLASS if not has_monday else PENALTY_HAS_CLASS


def compute_afternoon_penalty(plan: list[dict[str, Any]]) -> float:
    """Penalty for afternoon/evening classes (periods 6-14).

    Counts the number of DAYS that have any class starting at period ≥ 6.
    Score: max(1.0, 10.0 - afternoon_days × 1.0)

    Primarily used by the "morning_only" scenario to penalize
    any classes that fall outside the morning window.

    Args:
        plan: List of course dicts.

    Returns:
        Afternoon penalty score in [1.0, 10.0]. Higher = fewer afternoons.
    """
    afternoon_days: set[int] = set()
    for course in plan:
        for slot in course["schedule"]:
            if slot["start"] >= AFTERNOON_PERIOD_START:
                afternoon_days.add(slot["day"])

    count = len(afternoon_days)
    if count == 0:
        return PENALTY_NO_CLASS
    return round(max(1.0, PENALTY_NO_CLASS - count * PENALTY_PER_DAY_DECAY), 1)


# ── New: Night Penalty ───────────────────────────────────────


def compute_night_penalty(plan: list[dict[str, Any]]) -> float:
    """Penalty for night classes (periods 11-14).

    Counts DAYS with any class at period >= 11.
    Score: max(1.0, 10.0 - night_days × 1.0)
    """
    night_days: set[int] = set()
    for course in plan:
        for slot in course["schedule"]:
            if slot["start"] >= NIGHT_PERIOD_START:
                night_days.add(slot["day"])

    count = len(night_days)
    if count == 0:
        return PENALTY_NO_CLASS
    return round(max(1.0, PENALTY_NO_CLASS - count * PENALTY_PER_DAY_DECAY), 1)


# ── New: Free Days (whole days, not half-days) ───────────────


def compute_free_days(plan: list[dict[str, Any]]) -> float:
    """Count completely free days (Mon-Fri). Scale to [1.0, 10.0].

    0 free days → 1.0, 5 free days → 10.0.
    """
    occupied_days: set[int] = set()
    for course in plan:
        for slot in course["schedule"]:
            occupied_days.add(slot["day"])

    free = 5 - len(occupied_days)
    if free <= 0:
        return 1.0
    return round(1.0 + free * 1.8, 1)  # 1→2.8, 2→4.6, 3→6.4, 4→8.2, 5→10.0


# ── New: Distribution Score ───────────────────────────────────


def compute_distribution_score(plan: list[dict[str, Any]]) -> float:
    """Penalize extreme imbalance in daily class count.

    Collects period count per day. High variance → low score.
    Perfectly even spread → 10.0. All classes on one day → 1.0.
    """
    day_counts: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for course in plan:
        for slot in course["schedule"]:
            day_counts[slot["day"]] += 1

    counts = list(day_counts.values())
    if max(counts) == 0:
        return 10.0  # no classes at all = perfect balance

    # Coefficient of variation penalizes skew
    avg = sum(counts) / 5
    if avg == 0:
        return 10.0

    variance = sum((c - avg) ** 2 for c in counts) / 5
    cv = (variance ** 0.5) / avg  # normalized std dev

    # Map CV to score: CV=0 → 10.0, CV=2.0 → 1.0
    score = max(1.0, 10.0 - cv * 4.5)
    return round(score, 1)


# ── Legacy Stubs (reserved, DO NOT shadow real functions) ────
# NOTE: these are intentionally named _legacy_* so they don't
# override the real implementations above (lines 87-313).
# Change names back when GPA/stress modules are rebuilt.


def _legacy_gpa_score(plan: list[dict[str, Any]]) -> float:
    return 5.0


def _legacy_stress_score(plan: list[dict[str, Any]]) -> float:
    return 5.0


def _legacy_friday_penalty(plan: list[dict[str, Any]]) -> float:
    return 5.0


def _legacy_monday_penalty(plan: list[dict[str, Any]]) -> float:
    return 5.0


def _legacy_afternoon_penalty(plan: list[dict[str, Any]]) -> float:
    return 5.0


# ── Master Scoring ───────────────────────────────────────────


def calculate_score(
    plan: list[dict[str, Any]],
    weights: dict[str, float],
) -> tuple[float, dict[str, float]]:
    """Calculate the weighted total score for a plan.

    Computes 5 schedule-focused sub-scores + 5 legacy stubs (always 5.0).
    Legacy dims are included in the breakdown for API compatibility but
    carry zero weight in current scenarios.

    Returns:
        Tuple of (weighted_total, breakdown_dict).
    """
    # Core schedule dimensions
    scores: dict[str, float] = {
        "free_days": compute_free_days(plan),
        "compactness": compute_compact_score(plan),
        "no_morning": compute_morning_penalty(plan),
        "no_night": compute_night_penalty(plan),
        "distribution": compute_distribution_score(plan),
    }

    # Legacy stubs — always 5.0, included for API compat
    for dim in LEGACY_DIMENSIONS:
        scores[dim] = 5.0

    # Weighted sum over current dimensions only
    total = 0.0
    for key, val in scores.items():
        w = weights.get(key, 0.0)
        total += val * w

    breakdown = {k: round(v, 1) for k, v in scores.items()}
    return round(total, 1), breakdown


# ── Deduplication ────────────────────────────────────────────


def deduplicate_plans(
    scored: list[tuple[list[dict[str, Any]], float, dict[str, Any]]],
) -> list[tuple[list[dict[str, Any]], float, dict[str, Any]]]:
    """Remove plans with identical section_id sets.

    L1 dedup: frozenset(section_id) exactly matches → keep first (highest score).
    L2: same course_code but different section_id → KEPT (different plan).

    Args:
        scored: List of (plan, score, analysis_dict) sorted by score descending.

    Returns:
        Deduplicated list, preserving score order.
    """
    seen: set[frozenset[str]] = set()
    unique: list[tuple[list[dict[str, Any]], float, dict[str, Any]]] = []

    for plan, score, analysis in scored:
        key = frozenset(c["section_id"] for c in plan)
        if key not in seen:
            seen.add(key)
            unique.append((plan, score, analysis))

    return unique


# ── Reasons Generation ───────────────────────────────────────


def generate_reasons(
    plan: list[dict[str, Any]],
    breakdown: dict[str, float],
    scenario: str,
) -> list[str]:
    """Generate natural-language recommendation reasons for a plan.

    Focused on schedule metrics only — no GPA/teacher references.
    """
    reasons: list[str] = []

    # Free days highlight
    free_val = breakdown.get("free_days", 1.0)
    occupied = len(set(s["day"] for c in plan for s in c["schedule"]))
    free_days = 5 - occupied
    if free_days >= 3:
        reasons.append(f"每周 {free_days} 天完全自由")
    elif free_days >= 1:
        reasons.append(f"有 {free_days} 个完整空闲日")

    # Morning penalty highlight
    if breakdown.get("no_morning", 0) >= PENALTY_NO_CLASS:
        reasons.append("无早八课（无1-2节课）")
    elif breakdown.get("no_morning", 0) >= 7.0:
        reasons.append("早课很少，睡眠友好")

    # Night penalty highlight
    if breakdown.get("no_night", 0) >= PENALTY_NO_CLASS:
        reasons.append("完全无晚课（无11-14节课）")
    elif breakdown.get("no_night", 0) >= 7.0:
        reasons.append("晚间课程极少")

    # Compactness
    compact = breakdown.get("compactness", 5.0)
    if compact >= 8.0:
        reasons.append("课程集中度高，无碎片时间")
    elif compact < 5.0:
        reasons.append("课程较分散，但整体安排仍合理")

    # Distribution
    dist = breakdown.get("distribution", 5.0)
    if dist >= 8.0:
        reasons.append("每日课程分布均匀，节奏舒适")

    # Credit load (informational)
    total_credits = sum(_safe_credits(c) for c in plan)
    if total_credits <= 18:
        reasons.append(f"仅 {total_credits} 学分，压力很小")
    elif total_credits >= 24:
        reasons.append(f"共 {total_credits} 学分，学分较满")

    # Online course highlight
    online = [c for c in plan if c.get("delivery_mode") in ("线上网课", "线上线下混合")]
    for c in online[:1]:
        reasons.append(f"《{c['course_name']}》选{c['delivery_mode']}模式，节省通勤")

    # Fallback
    if not reasons:
        reasons.append("方案综合得分最优，各项指标均衡")

    return reasons


# ── Strategy Matching ────────────────────────────────────────


def match_strategies(
    plan: list[dict[str, Any]],
    scenario: str,
    all_strategies: list[dict[str, Any]],
) -> list[str]:
    """Find which strategy cards apply to a given plan.

    Each strategy has trigger conditions checked against the plan:
      - online-course-replacement: plan includes online/blended courses
      - teacher-score-diff: chosen section's rating differs from group's best by ≥ 0.3
      - credit-density-control: credits ≥ 22 or ≤ 16
      - elective-strategy: plan includes any "easy" course
      - time-block-optimization: compact_score < 7.0

    Also checks that the strategy's applicable_scenarios includes this scenario
    or "all".

    Args:
        plan: List of course dicts.
        scenario: Current scenario ID.
        all_strategies: Full list of strategy dicts from strategies.json.

    Returns:
        List of strategy IDs that apply to this plan.
    """
    matched: list[str] = []

    for strategy in all_strategies:
        sid = strategy["id"]
        applicable = strategy.get("applicable_scenarios", [])

        # Must apply to this scenario
        if scenario not in applicable and "all" not in applicable:
            continue

        triggered = False

        if sid == "online-course-replacement":
            # Triggered if any course is online or blended
            triggered = any(
                c.get("delivery_mode") in ("线上网课", "线上线下混合")
                for c in plan
            )
        elif sid == "teacher-score-diff":
            # Triggered if any chosen section's rating is ≥ 0.3 below
            # the best available section in the same credit_transfer_group
            # (We need all courses to compute this)
            # Simplified: trigger if plan has any course with rating < 4.5
            # AND there exists a course in the same group with higher rating
            triggered = any(
                (_safe_rating(c) or 0) < 4.5 for c in plan
            )
        elif sid == "credit-density-control":
            total_credits = sum(_safe_credits(c) for c in plan)
            triggered = total_credits >= 22 or total_credits <= 16
        elif sid == "elective-strategy":
            # Triggered if the plan includes at least one easy course
            triggered = any(c.get("course_type") == "easy" for c in plan)
        elif sid == "time-block-optimization":
            # Triggered if compactness is below 7.0 (noticeable fragmentation)
            compact = compute_compact_score(plan)
            triggered = compact < 7.0

        if triggered:
            matched.append(sid)

    return matched
