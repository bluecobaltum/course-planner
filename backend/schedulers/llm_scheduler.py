"""
LLMScheduler — AI-powered course selection via LLM.

Sends all available courses + scenario preference to the LLM,
gets back a selected course combination, validates hard constraints,
retries on failure, then scores through the existing engine.

SCHEDULER=llm activates this scheduler.

Model: controlled by LLM_EVAL_MODEL env var (default: DeepSeek-V4-Flash).
"""

import os
import json
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


# ── Helpers ────────────────────────────────────────────────


def _flatten_slots(course: dict[str, Any]) -> list[tuple[int, int, int]]:
    return [(s["day"], s["start"], s["end"]) for s in course["schedule"]]


def _has_conflict(a: dict[str, Any], b: dict[str, Any]) -> bool:
    for da, sa, ea in _flatten_slots(a):
        for db, sb, eb in _flatten_slots(b):
            if da == db and sa < eb and sb < ea:
                return True
    return False


def _validate_plan(
    selected: list[dict[str, Any]],
    courses: list[dict[str, Any]],
) -> list[str]:
    """Return list of error messages. Empty = valid."""
    errors = []

    # Check group mutual exclusion
    groups_seen: dict[str, str] = {}
    for c in selected:
        gid = c["credit_transfer_group"]
        if gid in groups_seen:
            errors.append(
                f"互斥组冲突: {c['section_id']}({c['course_name']}) 和 "
                f"{groups_seen[gid]} 同属 {gid} 组, 只能选一个"
            )
        groups_seen[gid] = c["section_id"]

    # Check time conflicts
    for i in range(len(selected)):
        for j in range(i + 1, len(selected)):
            if _has_conflict(selected[i], selected[j]):
                errors.append(
                    f"时间冲突: {selected[i]['section_id']}({selected[i]['course_name']}) 和 "
                    f"{selected[j]['section_id']}({selected[j]['course_name']})"
                )

    # Check required courses
    required_ids = [c["section_id"] for c in courses if c.get("required") is True]
    selected_ids = {c["section_id"] for c in selected}
    for rid in required_ids:
        if rid not in selected_ids:
            errors.append(f"缺少必选课程: {rid}")

    return errors


def _auto_resolve(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Greedy conflict resolver: keep first, drop later conflicting courses."""
    kept: list[dict[str, Any]] = []
    seen_groups: set[str] = set()
    for c in selected:
        if c["credit_transfer_group"] in seen_groups:
            continue
        if any(_has_conflict(c, k) for k in kept):
            continue
        kept.append(c)
        seen_groups.add(c["credit_transfer_group"])
    return kept


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
        ("plan_A", 1, "AI 推荐方案"),
        ("plan_B", 2, "AI 备选方案 B"),
        ("plan_C", 3, "AI 备选方案 C"),
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
            "school_days": len({s["day"] for c in selected for s in c["schedule"]}),
            "earliest_period": (
                min(s["start"] for c in selected for s in c["schedule"])
                if selected and any(c["schedule"] for c in selected)
                else 0
            ),
            "score_breakdown": breakdown,
            "reasons": reasons,
        },
        "matched_strategies": matched,
    }


def _format_courses_for_llm(
    courses: list[dict[str, Any]],
    scenario: str,
) -> str:
    """Build a compact course catalog + scenario preference for the LLM."""
    scenario_desc = {
        "balanced": "均衡模式——空闲时间、紧凑度、无早八均衡优化",
        "no_morning": "无早八模式——最大化减少1-2节早课，自然醒最重要",
        "compact": "紧凑模式——课程连续集中，减少碎片时间",
        "leisurely": "休闲模式——最大化空闲天数，课越少越好",
        "no_night": "无晚课模式——最大化减少11-14节晚课",
    }

    lines = [
        f"## 选课偏好: {scenario_desc.get(scenario, scenario)}",
        "",
        "## 可选课程列表",
    ]

    # Group by credit_transfer_group
    groups: dict[str, list[dict[str, Any]]] = {}
    for c in courses:
        gid = c["credit_transfer_group"]
        groups.setdefault(gid, []).append(c)

    for gid, sections in sorted(groups.items()):
        tag = "🔒必选组" if any(s.get("required") for s in sections) else ""
        lines.append(f"\n### 组 {gid} ({len(sections)}个平行班, 最多选1门) {tag}")
        for s in sections:
            slots_str = " ".join(
                f"周{sl['day']}{sl['start']}-{sl['end']}节"
                for sl in s["schedule"]
            )
            teacher = s["teacher"]["name"] if s.get("teacher") else "待定"
            required = " [必选]" if s.get("required") else ""
            lines.append(
                f"  {s['section_id']} | {s['course_name']} | "
                f"{teacher} | {slots_str} | {s['credits']}学分{required}"
            )

    lines.append(f"\n共 {len(courses)} 门课程, {len(groups)} 个课程组")

    return "\n".join(lines)


# ── Scheduler ────────────────────────────────────────────────


class LLMScheduler(BaseScheduler):
    """LLM-based course selector.

    Workflow:
      1. Format all courses + scenario preference → prompt
      2. Send to LLM, get back selected section_ids
      3. Validate hard constraints
      4. If invalid, retry with error feedback (up to 2 retries)
      5. Score through existing engine
    """

    MODEL = os.environ.get("LLM_EVAL_MODEL", "DeepSeek-V4-Flash")
    MAX_RETRIES = 1

    SYSTEM_PROMPT = """你是一个大学选课助手。根据用户偏好，从课程列表中选出最优课程组合。

规则:
1. 每个课程组最多选1门（平行班互斥）
2. 不能有时间冲突（同一天同一时段不能有两门课）
3. 标记为[必选]的课程必须选
4. 尽量多选课程，但冲突时优先保留更匹配偏好的

输出严格JSON格式:
{
  "reasoning": "一句话解释选择逻辑",
  "plans": [
    {"section_ids": ["PHY101-01", "MATH101-02", ...]}
  ]
}

只输出JSON，不要markdown代码块，不要解释。"""

    def _call_llm(self, prompt: str, model: str = "") -> dict[str, Any] | None:
        """Send prompt to LLM, parse JSON response."""
        from dotenv import load_dotenv; load_dotenv()
        from openai import OpenAI

        api_key = os.environ.get("OPENAI_API_KEY", "")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        client = OpenAI(api_key=api_key, base_url=base_url)

        effective_model = model or self.MODEL

        try:
            response = client.chat.completions.create(
                model=effective_model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=4096,
            )
            content = response.choices[0].message.content
            if not content:
                return None

            content = content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:])
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

            return json.loads(content)
        except Exception:
            return None

    def generate_plans(
        self,
        scenario: str,
        easy_count: int = 1,
        model_override: str = "",
        custom_prompt: str = "",
    ) -> list[dict[str, Any]]:
        model = model_override or self.MODEL
        courses = load_courses()
        all_strategies = load_strategies()
        scoring_weights = _SCORING_WEIGHTS.get(scenario, _SCORING_WEIGHTS["balanced"])
        course_by_id = {c["section_id"]: c for c in courses}

        base_prompt = _format_courses_for_llm(courses, scenario)

        # Inject custom user prompt if provided
        if custom_prompt:
            base_prompt = (
                "## 用户特殊偏好（优先遵循！）\n\n"
                + custom_prompt
                + "\n\n---\n\n"
                + base_prompt
            )

        prompt = base_prompt

        results: list[dict[str, Any]] = []

        for attempt in range(self.MAX_RETRIES + 1):
            raw = self._call_llm(prompt, model)
            if not raw:
                print(f"[LLM] Attempt {attempt}: _call_llm returned None", flush=True)
                continue

            # Support both single and multi-plan responses
            plan_sets = raw.get("plans", [])
            if not plan_sets and raw.get("section_ids"):
                plan_sets = [{"section_ids": raw["section_ids"]}]

            any_valid = False
            for rank, plan_set in enumerate(plan_sets[:1], start=1):
                section_ids = plan_set.get("section_ids", [])
                if not isinstance(section_ids, list) or not section_ids:
                    continue

                selected = [
                    course_by_id[sid]
                    for sid in section_ids
                    if sid in course_by_id
                ]
                if len(selected) < 3:
                    continue

                errors = _validate_plan(selected, courses)
                if errors:
                    selected = _auto_resolve(selected)
                    if len(selected) < 3:
                        if rank == 1:
                            errors_text = "\n".join(f"  - {e}" for e in errors)
                            retry_base = _format_courses_for_llm(courses, scenario)
                            if custom_prompt:
                                retry_base = "## 用户特殊偏好（优先遵循！）\n\n" + custom_prompt + "\n\n---\n\n" + retry_base
                            prompt = retry_base + f"\n\n❌ 前次选择有冲突:\n{errors_text}\n请修正后重新输出3套方案。"
                            break
                        continue

                plan = _build_plan(
                    selected, scenario, rank, all_strategies, scoring_weights
                )
                plan["llm_review"] = {
                    "overall": f"AI 选择理由: {raw.get('reasoning', '综合考虑课表优化')}",
                    "score": plan["score"],
                    "pros": [f"AI 从 {len(courses)} 门课中选出 {len(selected)} 门"],
                    "cons": [],
                    "suggestions": [],
                    "best_for": f"{scenario} 场景优化",
                }
                results.append(plan)
                any_valid = True

            if results:
                break

        return results
