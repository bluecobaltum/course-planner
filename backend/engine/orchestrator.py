"""
Plan generation orchestrator.

The main entry point `generate_plans(scenario, easy_count)` runs the full
pipeline: load → group → combine → fill → score → deduplicate → rank.

Hard constraints (violation = elimination):
  - Time conflict: no two courses overlap in schedule
  - Group mutual exclusion: one section per credit_transfer_group
  - Major coverage: every major group must have exactly one section
  - Credit range: 15 ≤ total_credits ≤ 25

Soft strategies affect SCORING only — no course is ever eliminated by preference.
"""

import random
from itertools import combinations, product
from typing import Any

from engine.loader import load_courses, load_strategies
from engine.scorer import (
    calculate_score,
    deduplicate_plans,
    generate_reasons,
    match_strategies,
)
from config.scenarios import SCENARIO_WEIGHTS, MIN_CREDITS, MAX_CREDITS


# ── Main Entry Point ─────────────────────────────────────────


def generate_plans(
    scenario: str,
    easy_count: int = 1,
) -> list[dict[str, Any]]:
    """Generate top-3 schedule plans for a given scenario.

    Full pipeline:
      1. Load all courses (no preference filtering — preferences affect
         SCORING only, not availability)
      2. Group by course_type → major_groups, easy_groups
      3. Cartesian product of major groups, prune by time conflict only
      4. Fill easy_count easy courses per major combo (top-2 random diversity)
      5. Filter by credit range [15, 25]
      6. Score all valid plans with scenario weights
      7. Deduplicate by frozenset(section_id)
      8. Sort by score descending, return top 3

    Args:
        scenario: Scenario ID, e.g. "no_morning", "gpa_focus".
        easy_count: Number of easy course groups to include (0-5, default 1).

    Returns:
        List of 0-3 plan dicts, each containing:
          - id, rank, score, label
          - courses (list of course dicts)
          - analysis (total_credits, school_days, earliest_period,
            score_breakdown, reasons)
          - matched_strategies (list of strategy IDs)
        Returns empty list if no feasible plan exists.
    """
    # ── Load data ──
    courses = load_courses()
    all_strategies = load_strategies()
    weights = SCENARIO_WEIGHTS[scenario]

    # ── Step 1: Group by course type ──
    major_groups, easy_groups = _group_by_course_type(courses)

    # Edge case: no major groups at all
    if not major_groups:
        return []

    # ── Step 2: Generate major-only combinations ──
    major_combos = _generate_major_combos(major_groups)

    if not major_combos:
        # All major combos have unresolvable time conflicts
        return []

    # ── Step 3: Fill easy courses + credit check ──
    plans: list[list[dict[str, Any]]] = []
    easy_group_ids = list(easy_groups.keys())
    effective_easy_count = min(easy_count, len(easy_group_ids))

    for combo in major_combos:
        filled = _fill_easy_courses(combo, easy_groups, effective_easy_count)
        for plan in filled:
            total_credits = sum(c["credits"] for c in plan)
            if MIN_CREDITS <= total_credits <= MAX_CREDITS:
                plans.append(plan)

    if not plans:
        # All combos fall outside credit range
        return []

    # ── Step 4: Score all plans ──
    scored: list[tuple[list[dict[str, Any]], float, dict[str, Any]]] = []
    for plan in plans:
        total_score, breakdown = calculate_score(plan, weights)
        reasons = generate_reasons(plan, breakdown, scenario)
        matched = match_strategies(plan, scenario, all_strategies)

        analysis = {
            "total_credits": sum(c["credits"] for c in plan),
            "school_days": _compute_school_days(plan),
            "earliest_period": _compute_earliest_period(plan),
            "score_breakdown": breakdown,
            "reasons": reasons,
        }
        scored.append((plan, total_score, {**analysis, "matched_strategies": matched}))

    # ── Step 5: Sort → Deduplicate → Top-3 ──
    scored.sort(key=lambda x: x[1], reverse=True)
    unique = deduplicate_plans(scored)
    top3 = unique[:3]

    # ── Step 6: Format response ──
    labels = [
        ("plan_A", 1, "推荐方案 A"),
        ("plan_B", 2, "备选方案 B"),
        ("plan_C", 3, "备选方案 C"),
    ]

    result: list[dict[str, Any]] = []
    for i, (plan, score, analysis) in enumerate(top3):
        plan_id, rank, label = labels[i]
        matched = analysis.pop("matched_strategies", [])
        result.append(
            {
                "id": plan_id,
                "rank": rank,
                "score": score,
                "label": label,
                "courses": plan,
                "analysis": analysis,
                "matched_strategies": matched,
            }
        )

    return result


# ── Grouping ─────────────────────────────────────────────────


def _group_by_course_type(
    courses: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    """Split courses into major and easy groups by credit_transfer_group.

    Args:
        courses: All course dicts from courses.json.

    Returns:
        Tuple of (major_groups, easy_groups).
        Each group is {credit_transfer_group_id: [course_dict, ...]}.
    """
    major_groups: dict[str, list[dict[str, Any]]] = {}
    easy_groups: dict[str, list[dict[str, Any]]] = {}

    for course in courses:
        group_id = course["credit_transfer_group"]
        if course["course_type"] == "major":
            if group_id not in major_groups:
                major_groups[group_id] = []
            major_groups[group_id].append(course)
        else:
            if group_id not in easy_groups:
                easy_groups[group_id] = []
            easy_groups[group_id].append(course)

    return major_groups, easy_groups


# ── Major Combination Generation ─────────────────────────────


def _generate_major_combos(
    major_groups: dict[str, list[dict[str, Any]]],
) -> list[list[dict[str, Any]]]:
    """Generate all conflict-free major course combinations.

    Takes the cartesian product of all major groups (one section per group)
    and prunes any combination with time conflicts.

    Args:
        major_groups: {group_id: [course_dict, ...]}.

    Returns:
        List of valid major-only course lists (each is a full major curriculum).
        May be empty if all combinations conflict.
    """
    group_lists = list(major_groups.values())
    valid_combos: list[list[dict[str, Any]]] = []

    for combo in product(*group_lists):
        # combo is a tuple of course dicts, one per group
        if not _has_time_conflict(list(combo)):
            valid_combos.append(list(combo))

    return valid_combos


# ── Easy Course Filling ──────────────────────────────────────


def _fill_easy_courses(
    base_combo: list[dict[str, Any]],
    easy_groups: dict[str, list[dict[str, Any]]],
    easy_count: int,
) -> list[list[dict[str, Any]]]:
    """Add easy courses to a major-only combo.

    For each combination of easy_count group IDs:
      1. From each selected group, pick the top-2 rated sections
      2. Randomly choose one (for diversity — not always the best)
      3. If it conflicts, try the other top-2 candidate
      4. If both conflict, skip that group (combo remains valid)

    Args:
        base_combo: A conflict-free major course list.
        easy_groups: {group_id: [course_dict, ...]}.
        easy_count: Number of easy groups to pick from.

    Returns:
        List of complete combos (major + easy). Each list is a valid plan
        candidate. Returns [base_combo] if easy_count == 0.
    """
    if easy_count == 0 or not easy_groups:
        return [base_combo]

    easy_group_ids = list(easy_groups.keys())
    effective_count = min(easy_count, len(easy_group_ids))

    results: list[list[dict[str, Any]]] = []

    for picked_ids in combinations(easy_group_ids, effective_count):
        easy_picks: list[dict[str, Any]] = []

        for gid in picked_ids:
            sections = easy_groups[gid]
            # Sort by rating descending, take top-2 for diversity
            sorted_sections = sorted(
                sections, key=lambda c: c["teacher"]["rating"], reverse=True
            )
            candidates = sorted_sections[:2]

            # Randomly pick from top-2 (NOT always the best)
            chosen = random.choice(candidates)
            if not _has_time_conflict(base_combo + easy_picks + [chosen]):
                easy_picks.append(chosen)
            else:
                # Try the other candidate
                others = [c for c in candidates if c["section_id"] != chosen["section_id"]]
                found = False
                for other in others:
                    if not _has_time_conflict(base_combo + easy_picks + [other]):
                        easy_picks.append(other)
                        found = True
                        break
                # If both conflict, this easy group is skipped
                # (the combo is still valid — just has one fewer easy course)

        results.append(base_combo + easy_picks)

    return results


# ── Conflict Detection ───────────────────────────────────────


def _has_time_conflict(courses: list[dict[str, Any]]) -> bool:
    """Check if any two courses overlap in time on the same day.

    Overlap condition: same day AND (a.start < b.end) AND (b.start < a.end).
    O(n²) over courses × O(m²) over schedule slots. For ≤ 8 courses this
    is negligible (< 1000 comparisons).

    Courses with empty schedules (async online) never conflict.

    Args:
        courses: List of course dicts, each with a "schedule" field.

    Returns:
        True if at least one pair of courses has overlapping time slots.
    """
    # Flatten all time slots: [(day, start, end), ...]
    slots: list[tuple[int, int, int]] = []
    for course in courses:
        for s in course["schedule"]:
            slots.append((s["day"], s["start"], s["end"]))

    # Compare all pairs
    for i in range(len(slots)):
        for j in range(i + 1, len(slots)):
            day_a, start_a, end_a = slots[i]
            day_b, start_b, end_b = slots[j]

            if day_a == day_b and start_a < end_b and start_b < end_a:
                return True

    return False


# ── Analysis Helpers ─────────────────────────────────────────


def _compute_school_days(plan: list[dict[str, Any]]) -> int:
    """Count distinct days that have at least one class.

    Args:
        plan: List of course dicts.

    Returns:
        Number of unique school days (1-5). 0 if all courses are async.
    """
    days: set[int] = set()
    for course in plan:
        for s in course["schedule"]:
            days.add(s["day"])
    return len(days)


def _compute_earliest_period(plan: list[dict[str, Any]]) -> int:
    """Find the earliest start period across the entire week.

    Args:
        plan: List of course dicts.

    Returns:
        Earliest period number (1-10). Returns 0 if all courses are async.
    """
    starts: list[int] = []
    for course in plan:
        for s in course["schedule"]:
            starts.append(s["start"])
    return min(starts) if starts else 0
