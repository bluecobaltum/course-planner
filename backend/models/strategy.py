"""Strategy data models.

Strategies are the core differentiator of this project — a knowledge base
of scientific course selection tips, each with future AI integration hooks.
"""

from typing import Optional

from pydantic import BaseModel, Field


class Strategy(BaseModel):
    """A course selection strategy / tip card.

    Each strategy has human-readable content for Demo display,
    plus trigger_condition and ai_prompt_fragment fields reserved
    for future LLM integration.
    """

    id: str = Field(..., min_length=1, description="Unique strategy identifier")
    category: str = Field(
        ...,
        description=(
            "Strategy category: 时间优化 | GPA优化 | "
            "压力管理 | 时间规划 | 选课技巧"
        ),
    )
    title: str = Field(..., min_length=1, description="Card title")
    summary: str = Field(..., min_length=1, description="One-line summary for card list")
    detail: str = Field(
        ..., min_length=1, description="Detailed explanation for expanded view"
    )
    icon: str = Field(..., min_length=1, description="Emoji icon, e.g. ⏱️")
    example: Optional[dict] = Field(
        default=None,
        description="Optional structured comparison data. Shape varies by strategy.",
    )
    applicable_scenarios: list[str] = Field(
        default_factory=list,
        description="Scenario IDs this strategy applies to. 'all' means all scenarios.",
    )
    difficulty: str = Field(
        ..., description="Implementation difficulty: 容易实施 | 需要提前规划 | 需要信息收集"
    )
    trigger_condition: Optional[dict] = Field(
        default=None,
        description=(
            "Future AI hook: keyword/scenario/goal matching rules "
            "that trigger this strategy's recommendation."
        ),
    )
    ai_prompt_fragment: Optional[str] = Field(
        default=None,
        description=(
            "Future AI hook: prompt fragment to inject into LLM "
            "when this strategy is triggered."
        ),
    )

    model_config = {
        "extra": "allow",
        "json_schema_extra": {
            "example": {
                "id": "online-course-replacement",
                "category": "时间优化",
                "title": "同课不同模式，时间差一倍",
                "summary": "公共课选网络班/混合班，上课频率降低50%+",
                "detail": "高等数学等公共课通常有多个平行班...",
                "icon": "⏱️",
                "applicable_scenarios": ["no_morning", "morning_only"],
                "difficulty": "容易实施",
            }
        },
    }
