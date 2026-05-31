"""
LLM-based plan evaluator — lets GPT-4o-mini review a schedule plan
and provide natural-language feedback, pros/cons, and suggestions.

Completely separate from the rule-based generate_reasons().
Falls back gracefully when no API key is set.
"""

import os
import json
from typing import Any


SYSTEM_PROMPT = """评估这份大学课表，输出JSON:
{"overall":"一句话总评","score":7.0,"pros":["优点"],"cons":["缺点"],"suggestions":["建议"],"best_for":"适合的学生类型"}

维度: 时间分布、早八(1-2节)、晚课(11-14节)、紧凑度、空闲日、总体合理性"""
# Total ~130 chars — fits in one message


def _get_client():
    from openai import OpenAI
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return OpenAI(api_key=api_key, base_url=base_url)


def _format_plan_for_llm(plan: dict[str, Any]) -> str:
    """Convert a plan dict into a compact schedule summary."""
    lines = []
    for c in plan["courses"]:
        slots_str = " ".join(
            f"周{s['day']}{s['start']}-{s['end']}节" for s in c["schedule"]
        )
        lines.append(f"{c['course_name']} | {slots_str}")

    total = sum(c.get("credits", 0) for c in plan["courses"])
    early = sum(1 for c in plan["courses"] for s in c["schedule"] if s["start"] <= 2)
    night = sum(1 for c in plan["courses"] for s in c["schedule"] if s["start"] >= 11)

    lines.append(f"总计{len(plan['courses'])}门 {total}学分 早八{early}节 晚课{night}节")
    return "\n".join(lines)


def evaluate_plan(plan: dict[str, Any], model_override: str = "") -> dict[str, Any] | None:

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None

    effective_model = model_override or os.environ.get("LLM_EVAL_MODEL", "Qwen3-32B")

    try:
        client = _get_client()
        schedule_text = _format_plan_for_llm(plan)
        combined = SYSTEM_PROMPT + "\n\n## 需要评估的课表\n\n" + schedule_text

        response = client.chat.completions.create(
            model=effective_model,
            messages=[
                {"role": "user", "content": combined},
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        content = response.choices[0].message.content
        if not content:
            return None

        # Strip markdown code fences if present
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:])
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        result = json.loads(content)

        # Validate
        result.setdefault("overall", "这是一份不错的课表")
        result.setdefault("score", 7.0)
        result.setdefault("pros", [])
        result.setdefault("cons", [])
        result.setdefault("suggestions", [])
        result.setdefault("best_for", "大部分学生")

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
