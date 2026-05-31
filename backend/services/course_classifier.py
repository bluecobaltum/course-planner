"""
Course classifier — auto-detects course category from keywords.

Categories:
  pe       — 体育课 (俱乐部, 体育, 球, 游泳, 健身, 跆拳道...)
  regular  — 普通课程 (专业必修/选修, default)

Used during import and manual course creation to auto-set
credit_transfer_group and course_type for PE courses.
"""

import re
from typing import Any

# ── PE Detection ────────────────────────────────────────────────

PE_KEYWORDS = [
    "俱乐部", "体育", "球", "游泳", "健身", "跆拳道", "武术",
    "瑜伽", "舞蹈", "田径", "体操", "太极", "散打", "击剑",
    "滑冰", "滑雪", "龙舟", "毽子", "跳绳", "户外运动",
    "男生", "女生",  # catch "男生体育课" etc
]

PE_NAME_PATTERN = re.compile("|".join(PE_KEYWORDS))


def detect_category(course: dict[str, Any]) -> str:
    """Return 'pe' or 'regular' based on course name/schedule/location.

    Detection order:
      1. Explicit field: course["category"] if present
      2. Name keywords: "俱乐部", "体育", "球", etc.
      3. Location: building contains "体育馆" or "体育场"
      4. Default: "regular"
    """
    # Explicit field takes priority
    if course.get("category") in ("pe", "regular"):
        return course["category"]

    name = course.get("course_name", "")
    if PE_NAME_PATTERN.search(name):
        return "pe"

    location = course.get("location")
    if isinstance(location, dict):
        building = location.get("building", "")
        if any(kw in building for kw in ["体育馆", "体育场", "操场"]):
            return "pe"

    return "regular"


def apply_classification(course: dict[str, Any]) -> dict[str, Any]:
    """Auto-classify and normalize a course dict.

    For PE courses:
      - Sets category='pe'
      - Sets credit_transfer_group='PE' (all PE courses share one group)
      - Sets course_type='easy'

    For regular courses:
      - Sets category='regular'
      - Keeps existing credit_transfer_group and course_type
    """
    category = detect_category(course)
    course["category"] = category

    if category == "pe":
        course["credit_transfer_group"] = "PE"
        if course.get("course_code"):
            course["course_code"] = "PE"
        course["course_type"] = "easy"
        # PE courses typically 1 credit unless specified
        if not course.get("credits") or course["credits"] <= 0:
            course["credits"] = 1

    return course
