"""
Excel course table parser.

Handles:
- Reading .xlsx/.xls files via openpyxl
- Fuzzy column name matching (Chinese headers)
- Time string parsing (周一1-2节,周三3-4节 → ScheduleSlot list)
- Converting rows to Course-compatible dicts
"""

import re
import io
from typing import Any

import openpyxl


# ── Column Name Mapping ─────────────────────────────────────────

# Each target field has a list of Chinese keywords to match against.
COLUMN_MAP: dict[str, list[str]] = {
    "course_name": ["课程名称", "课程名", "课程", "课名", "名称"],
    "course_code": ["课程代码", "课程编号", "代码", "编号", "课号"],
    "teacher_name": ["教师", "任课教师", "教师姓名", "老师", "授课教师", "上课教师"],
    "teacher_rating": ["评教", "评分", "评教分数", "教师评分", "学生评分", "rating"],
    "credits": ["学分", "学分数", "学时"],
    "schedule": ["上课时间", "时间", "上课安排", "时间安排", "周次时间", "节次"],
    "building": ["教学楼", "上课地点", "地点", "教室", "楼栋"],
    "room": ["教室号", "房间号", "房间", "教室"],
    "course_type": ["课程类型", "课程类别", "类型", "类别", "性质", "必修/选修"],
    "delivery_mode": ["授课模式", "教学模式", "上课方式", "授课方式", "模式"],
    "section_id": ["教学班号", "班号", "选课编号", "课序号"],
}


def _fuzzy_match(headers: list[str]) -> dict[str, int]:
    """Match Excel column headers to target fields via keyword lookup.

    Returns {target_field: column_index} for matched columns.
    """
    mapping: dict[str, int] = {}
    for idx, header in enumerate(headers):
        h = str(header).strip().lower()
        for field, keywords in COLUMN_MAP.items():
            if field in mapping:
                continue  # already matched
            for kw in keywords:
                if kw in h or h in kw:
                    mapping[field] = idx
                    break
    return mapping


# ── Time String Parser ───────────────────────────────────────────

DAY_MAP = {
    "周一": 1, "星期一": 1, "周1": 1, "mon": 1,
    "周二": 2, "星期二": 2, "周2": 2, "tue": 2,
    "周三": 3, "星期三": 3, "周3": 3, "wed": 3,
    "周四": 4, "星期四": 4, "周4": 4, "thu": 4,
    "周五": 5, "星期五": 5, "周5": 5, "fri": 5,
}

DAY_PATTERN = re.compile(
    r"(周一|周二|周三|周四|周五|星期一|星期二|星期三|星期四|星期五|周[1-5])"
)
PERIOD_PATTERN = re.compile(r"(\d{1,2})\s*[-–—节至到]\s*(\d{1,2})\s*节")


def parse_time_string(text: str) -> list[dict[str, int]]:
    """Parse a Chinese time description into ScheduleSlot list.

    Examples:
        "周一1-2节,周三3-4节" → [{"day":1,"start":1,"end":2}, {"day":3,"start":3,"end":4}]
        "周二 第3-4节"        → [{"day":2,"start":3,"end":4}]

    Returns empty list for async/online courses.
    """
    if not text or not isinstance(text, str):
        return []

    text = str(text).strip()
    if text in ("无", "无固定时间", "异步", "异步网课", "线上", "无固定时间（异步网课）"):
        return []

    slots: list[dict[str, int]] = []

    # Try to find day-period pairs
    # Strategy: split by day keywords, then find period ranges nearby
    parts = re.split(r"[,，、;\s]+", text)
    current_day: int | None = None

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Check for day name
        day_match = DAY_PATTERN.search(part)
        if day_match:
            for key, val in DAY_MAP.items():
                if key in part:
                    current_day = val
                    break

        # Check for period range
        period_match = PERIOD_PATTERN.search(part)
        if period_match and current_day is not None:
            start = int(period_match.group(1))
            end = int(period_match.group(2))
            if 1 <= start <= 14 and 1 <= end <= 14 and end >= start:
                slots.append({"day": current_day, "start": start, "end": end})

    # Fallback: try simpler pattern "周X A-B节" anywhere in text
    if not slots:
        simpler = re.findall(
            r"(周[一二三四五1-5]).*?(\d{1,2})\s*[-–—节至到]\s*(\d{1,2})\s*节",
            text,
        )
        for day_str, s, e in simpler:
            day_val = 0
            for k, v in DAY_MAP.items():
                if k in day_str:
                    day_val = v
                    break
            if day_val and 1 <= int(s) <= 14 and 1 <= int(e) <= 14:
                slots.append({"day": day_val, "start": int(s), "end": int(e)})

    return slots


# ── Type Detection ───────────────────────────────────────────────

def _detect_course_type(name: str, type_str: str) -> str:
    """Detect major vs easy from type string or course name."""
    if type_str:
        t = str(type_str).strip()
        if any(kw in t for kw in ["必修", "专业课", "专业", "major", "核心", "学位"]):
            return "major"
        if any(kw in t for kw in ["选修", "通识", "公选", "水课", "easy", "任选"]):
            return "easy"
    # Heuristic from name
    if name:
        n = str(name)
        if any(kw in n for kw in ["体育", "艺术", "鉴赏", "导论", "概论"]):
            return "easy"
    return "major"


def _detect_delivery_mode(location_str: str, mode_str: str) -> str:
    """Detect delivery mode from strings."""
    if mode_str:
        m = str(mode_str).strip()
        if any(kw in m for kw in ["线上", "网课", "网络", "在线", "online"]):
            if any(kw in m for kw in ["混合", "blend", "混合式"]):
                return "线上线下混合"
            return "线上网课"
    if location_str:
        l = str(location_str).strip()
        if any(kw in l for kw in ["线上", "网络", "在线", "网课", "无", "-", "—"]):
            return "线上网课"
    return "线下传统"


# ── Main Parser ──────────────────────────────────────────────────

def parse_excel(file_content: bytes, filename: str = "") -> list[dict[str, Any]]:
    """Parse an Excel file into a list of Course-compatible dicts.

    Args:
        file_content: Raw bytes of the Excel file.
        filename: Original filename (for extension detection).

    Returns:
        List of course dicts matching the Course model shape.
    """
    wb = openpyxl.load_workbook(io.BytesIO(file_content), data_only=True)
    ws = wb.active

    # Read all rows
    rows: list[list[Any]] = []
    for row in ws.iter_rows(values_only=True):
        rows.append(list(row))

    if len(rows) < 2:
        return []

    # First row = headers
    headers = [str(c).strip() if c is not None else "" for c in rows[0]]
    mapping = _fuzzy_match(headers)

    # Must have at least course_name mapped
    if "course_name" not in mapping:
        # Fallback: use first column as course_name
        mapping["course_name"] = 0

    def _get(row: list[Any], field: str) -> str:
        idx = mapping.get(field)
        if idx is not None and idx < len(row) and row[idx] is not None:
            return str(row[idx]).strip()
        return ""

    def _get_int(row: list[Any], field: str, default: int = 3) -> int:
        idx = mapping.get(field)
        if idx is not None and idx < len(row) and row[idx] is not None:
            try:
                return int(float(str(row[idx])))
            except (ValueError, TypeError):
                pass
        return default

    def _get_float(row: list[Any], field: str, default: float = 4.0) -> float | None:
        idx = mapping.get(field)
        if idx is not None and idx < len(row) and row[idx] is not None:
            try:
                return float(str(row[idx]))
            except (ValueError, TypeError):
                pass
        return default

    courses: list[dict[str, Any]] = []
    for i, row in enumerate(rows[1:], start=2):
        # Skip fully empty rows
        if all(c is None or str(c).strip() == "" for c in row):
            continue

        name = _get(row, "course_name")
        if not name:
            continue

        code = _get(row, "course_code") or _get(row, "section_id") or f"COURSE{i:03d}"
        section_id = _get(row, "section_id") or f"{code}-01"
        group = _get(row, "course_code") or code
        credits = _get_int(row, "credits", 3)
        teacher_name = _get(row, "teacher_name")
        rating = _get_float(row, "teacher_rating", 4.0)

        # Schedule
        schedule_str = _get(row, "schedule")
        schedule = parse_time_string(schedule_str)

        # Location
        building = _get(row, "building")
        room = _get(row, "room")
        floor_val = 1
        # Try to extract floor from room number (e.g. "301" → floor 3)
        if room and room[0].isdigit():
            floor_val = int(room[0])

        # Type & mode
        type_str = _get(row, "course_type")
        course_type = _detect_course_type(name, type_str)
        delivery = _detect_delivery_mode(
            _get(row, "building"), _get(row, "delivery_mode")
        )

        course: dict[str, Any] = {
            "section_id": section_id,
            "course_code": code,
            "course_name": name,
            "credit_transfer_group": group,
            "credits": credits,
            "teacher": {
                "name": teacher_name,
                "rating": rating,
            }
            if teacher_name
            else None,
            "schedule": schedule,
            "location": {
                "building": building,
                "floor": floor_val,
                "room": room,
            }
            if (building or room)
            else None,
            "course_type": course_type,
            "delivery_mode": delivery,
            "semester": "2025-2026-2",
        }
        courses.append(course)

    return courses
