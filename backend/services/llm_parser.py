"""
LLM-based course text parser using GPT-4o-mini.

Sends free-form Chinese course description to the LLM and receives
structured Course-compatible JSON. Retries once on JSON parse failure.
"""

import json
import os
from typing import Any

from openai import OpenAI

# ── Configuration ────────────────────────────────────────────────

MODEL = "gpt-4o-mini"
MAX_RETRIES = 1

SYSTEM_PROMPT = """你是一个课程数据解析器。从用户输入的文本中提取所有课程信息。

对于每门课程，输出以下 JSON 字段：
- section_id: 课程代码-班号（如 MATH101-01），无法确定时用课程代码-01
- course_code: 课程代码（如 MATH101）
- course_name: 课程中文名（如 高等数学A）
- credit_transfer_group: 学分互认组，默认等于 course_code
- credits: 学分数（整数，默认3）
- teacher: {"name": "教师名", "rating": 评分(1-5)} 或 null
- schedule: [{"day": 1-5(周一=1..周五=5), "start": 1-14, "end": 1-14}] 或 []
- location: {"building": "教学楼", "floor": 楼层(int), "room": "教室号"} 或 null
- course_type: "major"（专业课）或 "easy"（选修/水课）
- delivery_mode: "线下传统" 或 "线上网课" 或 "线上线下混合"
- semester: "2025-2026-2"

节次规则：
- 上午 = 第1-5节
- 下午 = 第6-10节
- 晚上 = 第11-14节
- 早八 = 第1-2节

时间描述转换示例：
- "周一1-2节" → {"day": 1, "start": 1, "end": 2}
- "周三6-8节" → {"day": 3, "start": 6, "end": 8}
- "周五11-13节" → {"day": 5, "start": 11, "end": 13}
- "无固定时间" → []

输出必须是严格的 JSON 数组，不要包含任何解释文字。"""


def _get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", None)
    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def parse_course_text(text: str) -> list[dict[str, Any]]:
    """Parse free-form Chinese course text into structured course dicts.

    Args:
        text: User-provided course descriptions (Chinese).

    Returns:
        List of course dicts compatible with the Course Pydantic model.

    Raises:
        ValueError: If parsing fails after retries or no API key is set.
    """
    if not text or not text.strip():
        raise ValueError("输入文本为空")

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        # Fallback: basic regex extraction when no API key
        return _fallback_parse(text)

    client = _get_client()

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,
                max_tokens=4096,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("LLM 返回空内容")

            # Parse JSON — handle both array and {courses: [...]} wrappers
            data = json.loads(content)
            if isinstance(data, dict):
                courses = data.get("courses", [])
                if not courses:
                    # Maybe the dict IS a single course
                    if "course_name" in data:
                        courses = [data]
            elif isinstance(data, list):
                courses = data
            else:
                raise ValueError(f"LLM 返回了非预期的格式: {type(data)}")

            # Validate and fill defaults
            return [_normalize_course(c) for c in courses if isinstance(c, dict)]

        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                continue
        except Exception as e:
            last_error = e
            break

    raise ValueError(f"课程解析失败: {last_error}")


def _normalize_course(raw: dict[str, Any]) -> dict[str, Any]:
    """Ensure a parsed course dict has all required fields with valid defaults."""
    code = str(raw.get("course_code", raw.get("section_id", "UNKNOWN")))
    section_id = str(raw.get("section_id", f"{code}-01"))
    name = str(raw.get("course_name", "未命名课程"))
    group = str(raw.get("credit_transfer_group", code))
    credits_val = raw.get("credits")
    try:
        credits = int(float(str(credits_val))) if credits_val is not None else 3
    except (ValueError, TypeError):
        credits = 3
    credits = max(1, min(10, credits))

    teacher = raw.get("teacher")
    if isinstance(teacher, dict) and teacher.get("name"):
        try:
            r = teacher.get("rating")
            rating = float(str(r)) if r is not None else 4.0
        except (ValueError, TypeError):
            rating = 4.0
        teacher = {
            "name": str(teacher["name"]),
            "rating": max(1.0, min(5.0, rating)),
        }
    else:
        teacher = None

    schedule = raw.get("schedule", [])
    if not isinstance(schedule, list):
        schedule = []
    normalized_slots = []
    for slot in schedule:
        if isinstance(slot, dict):
            try:
                d = int(float(str(slot.get("day", 1)))) if slot.get("day") is not None else 1
                s = int(float(str(slot.get("start", 1)))) if slot.get("start") is not None else 1
                e = int(float(str(slot.get("end", s)))) if slot.get("end") is not None else s
            except (ValueError, TypeError):
                continue
            if 1 <= d <= 5 and 1 <= s <= 14 and 1 <= e <= 14 and e >= s:
                normalized_slots.append({"day": d, "start": s, "end": e})
    schedule = normalized_slots

    location = raw.get("location")
    if isinstance(location, dict) and (location.get("building") or location.get("room")):
        try:
            f = location.get("floor")
            floor_val = int(float(str(f))) if f is not None else 1
        except (ValueError, TypeError):
            floor_val = 1
        location = {
            "building": str(location.get("building", "-")),
            "floor": floor_val,
            "room": str(location.get("room", "-")),
        }
    else:
        location = None

    course_type = str(raw.get("course_type", "major"))
    if course_type not in ("major", "easy"):
        course_type = "major"

    delivery = str(raw.get("delivery_mode", "线下传统"))
    if delivery not in ("线下传统", "线上网课", "线上线下混合"):
        delivery = "线下传统"

    return {
        "section_id": section_id,
        "course_code": code,
        "course_name": name,
        "credit_transfer_group": group,
        "credits": credits,
        "teacher": teacher,
        "schedule": schedule,
        "location": location,
        "course_type": course_type,
        "delivery_mode": delivery,
        "semester": "2025-2026-2",
    }


# ── Fallback Parser (no API key) ─────────────────────────────────

def _fallback_parse(text: str) -> list[dict[str, Any]]:
    """Basic regex-based parser when OpenAI API key is unavailable.

    Detects common Chinese course description patterns:
        课程名 教师名 周X A-B节 周Y C-D节
    """
    import re

    courses: list[dict[str, Any]] = []
    # Split by lines or common delimiters
    lines = re.split(r"[\n\r;；]+", text)

    for idx, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 4:
            continue

        # Try to extract: course name, teacher, and schedule
        name_match = re.search(
            r"([一-鿿\w]+(?:[（(][一-鿿\w]+[)）])?(?:[A-C])?)",
            line,
        )
        name = name_match.group(1) if name_match else f"课程{idx + 1}"

        teacher_match = re.search(r"([一-鿿]{2,4})(?:老师|教授|教师)?", line)
        teacher_name = teacher_match.group(1) if teacher_match else ""

        # Parse schedule slots
        from services.excel_parser import parse_time_string

        slots = parse_time_string(line)

        code = name[:6].upper().replace(" ", "")
        courses.append(
            {
                "section_id": f"{code}-01",
                "course_code": code,
                "course_name": name,
                "credit_transfer_group": code,
                "credits": 3,
                "teacher": {"name": teacher_name, "rating": 4.0} if teacher_name else None,
                "schedule": slots,
                "location": None,
                "course_type": "major",
                "delivery_mode": "线下传统",
                "semester": "2025-2026-2",
            }
        )

    return courses if courses else []
