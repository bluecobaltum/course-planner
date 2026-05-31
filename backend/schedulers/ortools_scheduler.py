"""
ORToolsScheduler — Two-phase lexicographic CP-SAT optimization.

Phase 1: Maximize course count (coverage).
Phase 2: Among max-coverage solutions, minimize scenario penalties.

This guarantees the solver always picks the maximum feasible course set,
then optimizes for morning/night/friday preferences within that.
"""

from typing import Any

from engine.loader import load_courses, load_strategies
from engine.scorer import (
    calculate_score,
    generate_reasons,
    match_strategies,
    _safe_credits,
)
from config.scenarios import SCENARIO_WEIGHTS as _SCORING_WEIGHTS
from schedulers.base import BaseScheduler
from schedulers.scheduler_weights import get_weights as _get_ortools_weights


# ── Helpers ──────────────────────────────────────────────────────


def _flatten_slots(course: dict[str, Any]) -> list[tuple[int, int, int]]:
    return [(s["day"], s["start"], s["end"]) for s in course["schedule"]]


def _has_conflict(a: dict[str, Any], b: dict[str, Any]) -> bool:
    for da, sa, ea in _flatten_slots(a):
        for db, sb, eb in _flatten_slots(b):
            if da == db and sa < eb and sb < ea:
                return True
    return False


def _school_days(plan: list[dict[str, Any]]) -> int:
    return len({s["day"] for c in plan for s in c["schedule"]})


def _earliest_period(plan: list[dict[str, Any]]) -> int:
    starts = [s["start"] for c in plan for s in c["schedule"]]
    return min(starts) if starts else 0


def _build_plan(
    selected: list[dict[str, Any]],
    scenario: str,
    rank: int,
    all_strategies: list[dict[str, Any]],
    scoring_weights: dict[str, float],
) -> dict[str, Any]:
    total_score, breakdown = calculate_score(selected, scoring_weights)
    reasons = generate_reasons(selected, breakdown, scenario)
    matched = match_strategies(selected, scenario, all_strategies)

    labels = [
        ("plan_A", 1, "推荐方案 A"),
        ("plan_B", 2, "备选方案 B"),
        ("plan_C", 3, "备选方案 C"),
    ]
    plan_id, rk, label = labels[min(rank - 1, 2)]

    return {
        "id": plan_id,
        "rank": rk,
        "score": total_score,
        "label": label,
        "courses": selected,
        "analysis": {
            "total_credits": sum(_safe_credits(c) for c in selected),
            "school_days": _school_days(selected),
            "earliest_period": _earliest_period(selected),
            "score_breakdown": breakdown,
            "reasons": reasons,
        },
        "matched_strategies": matched,
    }


# ── Scheduler ────────────────────────────────────────────────────


class ORToolsScheduler(BaseScheduler):
    """Two-phase CP-SAT scheduler.

    Phase 1: maximize course count (hard constraint: group picks, conflicts, required).
    Phase 2: fix coverage at max, minimize scenario-specific penalties.

    This eliminates the "coverage vs penalty" trade-off — the solver
    always picks as many courses as possible first.
    """

    def generate_plans(
        self,
        scenario: str,
        easy_count: int = 1,
    ) -> list[dict[str, Any]]:
        from ortools.sat.python import cp_model

        courses = load_courses()
        all_strategies = load_strategies()
        scoring_weights = _SCORING_WEIGHTS.get(scenario, _SCORING_WEIGHTS["balanced"])
        or_weights = _get_ortools_weights(scenario)

        # ── Group courses ──
        all_groups: dict[str, list[int]] = {}
        course_map: dict[int, dict[str, Any]] = {}
        all_indices: list[int] = []

        for i, c in enumerate(courses):
            course_map[i] = c
            all_indices.append(i)
            gid = c["credit_transfer_group"]
            all_groups.setdefault(gid, []).append(i)

        if not all_groups:
            return []

        # ── Conflict pairs ──
        conflict_pairs: list[tuple[int, int]] = []
        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                if _has_conflict(courses[i], courses[j]):
                    conflict_pairs.append((i, j))

        # ── Build base constraints (shared across phases) ──
        def _add_base_constraints(model, x):
            # C1: at most one per group
            for indices in all_groups.values():
                model.Add(sum(x[i] for i in indices) <= 1)
            # C2: required courses must be selected
            for i in all_indices:
                if courses[i].get("required") is True:
                    model.Add(x[i] == 1)
            # C3: no time conflicts
            for i, j in conflict_pairs:
                model.Add(x[i] + x[j] <= 1)
            # C4: at least 3 courses
            model.Add(sum(x[i] for i in all_indices) >= 3)

        # ── Build scenario objective terms ──
        def _add_scenario_objective(model, x):
            """Return list of (weight, var) for scenario-specific penalties."""
            obj_terms = []

            # Early-morning penalty
            for i in all_indices:
                c = courses[i]
                if any(s["start"] <= 2 for s in c["schedule"]):
                    obj_terms.append((or_weights["early"], x[i]))

            # Night penalty
            for i in all_indices:
                c = courses[i]
                if any(s["start"] >= 11 for s in c["schedule"]):
                    obj_terms.append((or_weights["night"], x[i]))

            # Friday bonus
            friday_indices = [
                i for i in all_indices
                if any(s["day"] == 5 for s in courses[i]["schedule"])
            ]
            friday_free = model.NewBoolVar("friday_free")
            if friday_indices:
                has_friday = model.NewBoolVar("has_friday")
                model.Add(sum(x[i] for i in friday_indices) >= 1).OnlyEnforceIf(has_friday)
                model.Add(sum(x[i] for i in friday_indices) == 0).OnlyEnforceIf(has_friday.Not())
                model.Add(friday_free == 1 - has_friday)
            else:
                model.Add(friday_free == 1)
            obj_terms.append((-or_weights["friday"], friday_free))

            return obj_terms

        # ── Multi-pass solve ──
        results: list[dict[str, Any]] = []
        excluded: list[list[int]] = []
        MAX_PLANS = 3

        for plan_rank in range(1, MAX_PLANS + 1):
            # ── Phase 1: maximize coverage ──
            model1 = cp_model.CpModel()
            x1 = {i: model1.NewBoolVar(f"x1_{i}") for i in all_indices}
            _add_base_constraints(model1, x1)
            # Exclude previous solutions
            for prev_set in excluded:
                prev_vars = [x1[i] for i in prev_set if i in x1]
                not_prev_vars = [x1[i] for i in all_indices if i not in prev_set]
                if prev_vars and not_prev_vars:
                    model1.Add(sum(1 - v for v in prev_vars) + sum(v for v in not_prev_vars) >= 1)

            model1.Maximize(sum(x1[i] for i in all_indices))

            solver1 = cp_model.CpSolver()
            solver1.parameters.max_time_in_seconds = 5.0
            solver1.parameters.num_search_workers = 4
            status1 = solver1.Solve(model1)

            if status1 not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                break

            max_coverage = int(solver1.ObjectiveValue())

            # ── Phase 2: fix coverage, minimize scenario penalties ──
            model2 = cp_model.CpModel()
            x2 = {i: model2.NewBoolVar(f"x2_{i}") for i in all_indices}
            _add_base_constraints(model2, x2)
            # Exclude previous solutions
            for prev_set in excluded:
                prev_vars = [x2[i] for i in prev_set if i in x2]
                not_prev_vars = [x2[i] for i in all_indices if i not in prev_set]
                if prev_vars and not_prev_vars:
                    model2.Add(sum(1 - v for v in prev_vars) + sum(v for v in not_prev_vars) >= 1)

            # Fix coverage at max
            model2.Add(sum(x2[i] for i in all_indices) == max_coverage)

            # Scenario objective
            obj_terms2 = _add_scenario_objective(model2, x2)
            if obj_terms2:
                model2.Minimize(sum(w * v for w, v in obj_terms2))

            solver2 = cp_model.CpSolver()
            solver2.parameters.max_time_in_seconds = 5.0
            solver2.parameters.num_search_workers = 4
            status2 = solver2.Solve(model2)

            if status2 not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                break

            selected_indices = [i for i in all_indices if solver2.Value(x2[i]) == 1]
            if not selected_indices:
                break

            excluded.append(selected_indices)

            plan = _build_plan(
                [course_map[i] for i in selected_indices],
                scenario, plan_rank, all_strategies, scoring_weights,
            )
            results.append(plan)

        return results
