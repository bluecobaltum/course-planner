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
    SCENARIO_WEIGHTS,
    MIN_CREDITS,
    MAX_CREDITS,
    STRESS_COMFORT_CREDITS,
    STRESS_MODERATE_CREDITS,
    COMPACT_FRAGMENT_DECAY,
    MORNING_PERIOD_START,
    MORNING_PERIOD_END,
    AFTERNOON_PERIOD_START,
    AFTERNOON_PERIOD_END,
    PENALTY_NO_CLASS,
    PENALTY_HAS_CLASS,
    PENALTY_PER_DAY_DECAY,
    EARLY_MORNING_CUTOFF,
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


def compute_free_score(plan: list[dict[str, Any]]) -> float:
    """Count completely free half-days across the week.

    A half-day is "free" if NO occupied periods fall in its range.
    Morning = periods 1-5, Afternoon+Evening = periods 6-14.
    An entirely empty day contributes 2 free half-days.

    Uses _get_occupied_periods to correctly handle cross-session courses
    (e.g., a course at periods 3-6 blocks BOTH morning and afternoon).

    Args:
        plan: List of course dicts.

    Returns:
        Free half-day count, naturally 0-10 (5 days × 2 half-days).
    """
    occupied = _get_occupied_periods(plan)
    free_count = 0

    for day in range(1, 6):  # Mon-Fri
        periods = occupied.get(day, set())

        if not periods:
            # Entirely free day
            free_count += 2
            continue

        # Morning (periods 1-5) free?
        morning_occupied = any(
            MORNING_PERIOD_START <= p <= MORNING_PERIOD_END for p in periods
        )
        if not morning_occupied:
            free_count += 1

        # Afternoon (periods 6-14) free?
        afternoon_occupied = any(
            AFTERNOON_PERIOD_START <= p <= AFTERNOON_PERIOD_END for p in periods
        )
        if not afternoon_occupied:
            free_count += 1

    return float(min(10, free_count))


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


# ── Master Scoring ───────────────────────────────────────────


def calculate_score(
    plan: list[dict[str, Any]],
    weights: dict[str, float],
) -> tuple[float, dict[str, float]]:
    """Calculate the weighted total score for a plan.

    Computes all 8 sub-scores, then applies scenario-specific weights.
    Uses direct key access (weights["key"]) — missing keys raise KeyError
    to catch config errors at development time.

    Args:
        plan: List of course dicts representing one complete schedule.
        weights: Scenario weight dict with exactly 8 keys.

    Returns:
        Tuple of (weighted_total, breakdown_dict).
        total is rounded to 1 decimal, breakdown values to 1 decimal.
    """
    # Compute all 8 sub-scores
    scores: dict[str, float] = {
        "gpa_score": compute_gpa_score(plan),
        "compact_score": compute_compact_score(plan),
        "stress_score": compute_stress_score(plan),
        "free_score": compute_free_score(plan),
        "morning_penalty": compute_morning_penalty(plan),
        "friday_penalty": compute_friday_penalty(plan),
        "monday_penalty": compute_monday_penalty(plan),
        "afternoon_penalty": compute_afternoon_penalty(plan),
    }

    # Weighted sum — direct key access, no .get() fallback
    total = sum(scores[key] * weights[key] for key in scores)

    # Round for clean display
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

    Rules are checked in order. Each rule contributes at most one reason.
    Produces 2-5 bullet points suitable for frontend display.

    Args:
        plan: List of course dicts.
        breakdown: Score breakdown dict from calculate_score.
        scenario: Scenario ID (for context-aware reason generation).

    Returns:
        List of Chinese natural-language reason strings.
    """
    reasons: list[str] = []

    # ── Penalty-based highlights ──
    if breakdown["morning_penalty"] >= PENALTY_NO_CLASS:
        reasons.append("无早八课（无1-2节课）")
    if breakdown["friday_penalty"] >= PENALTY_NO_CLASS:
        reasons.append("周五全空，享受长周末")
    if breakdown["monday_penalty"] >= PENALTY_NO_CLASS:
        reasons.append("周一全空，三天小长假")
    if breakdown["afternoon_penalty"] >= PENALTY_NO_CLASS:
        reasons.append("下午/晚间完全自由")

    # ── Teacher quality ──
    ratings = [_safe_rating(c) for c in plan if _safe_rating(c) is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    if avg_rating >= 4.5:
        reasons.append(f"教师平均评分 {avg_rating:.1f}，整体质量优秀")
    elif avg_rating >= 4.0:
        reasons.append(f"教师平均评分 {avg_rating:.1f}，质量良好")

    # ── Credit load ──
    total_credits = sum(_safe_credits(c) for c in plan)
    if total_credits <= 18:
        reasons.append(f"仅 {total_credits} 学分，学业压力很小")
    elif total_credits >= 24:
        reasons.append(f"共 {total_credits} 学分，学分较满但收益高")

    # ── Delivery mode highlights ──
    online_courses = [
        c
        for c in plan
        if c.get("delivery_mode") in ("线上网课", "线上线下混合")
    ]
    for c in online_courses[:2]:  # at most 2
        reasons.append(f"《{c['course_name']}》选{c['delivery_mode']}模式，节省通勤时间")

    # ── Compactness ──
    if breakdown["compact_score"] >= 8.0:
        reasons.append("课程集中度高，无碎片时间")
    elif breakdown["compact_score"] < 5.0:
        reasons.append("课程较分散，但整体安排仍合理")

    # ── Scenario-specific highlights ──
    if scenario == "gpa_focus" and avg_rating >= 4.5:
        reasons.append("GPA友好度高，教师评分优秀")
    elif scenario == "easy_mode" and total_credits <= 20:
        reasons.append("轻松模式：学分适中，压力可控")
    elif scenario == "morning_only" and breakdown["afternoon_penalty"] >= 8.0:
        reasons.append("上午集中度高，下午时间完全自主")

    # ── Fallback ──
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
