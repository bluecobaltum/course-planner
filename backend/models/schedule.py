"""Schedule output data models.

These models define the shape of a generated schedule plan —
the scored, analyzed output that the frontend receives.
"""

from typing import Optional

from pydantic import BaseModel, Field

from models.course import Course


class ScoreBreakdown(BaseModel):
    """Schedule-focused scoring dimensions + legacy stubs.

    All scores in [1.0, 10.0]. Higher is always better.
    """

    # Current schedule-optimizer dimensions
    free_days: float = Field(default=5.0, description="Free whole days score (1.0-10.0)")
    compactness: float = Field(default=5.0, description="Schedule compactness (1.0-10.0)")
    no_morning: float = Field(default=5.0, description="No-early-morning score (10.0 = perfect)")
    no_night: float = Field(default=5.0, description="No-night-class score (10.0 = perfect)")
    distribution: float = Field(default=5.0, description="Daily balance score (10.0 = even spread)")

    # Legacy stubs (reserved, always 5.0)
    gpa_score: float = Field(default=5.0, description="[Legacy] GPA score stub")
    compact_score: float = Field(default=5.0, description="[Legacy] Compactness stub")
    stress_score: float = Field(default=5.0, description="[Legacy] Stress score stub")
    free_score: float = Field(default=5.0, description="[Legacy] Free half-day score stub")
    morning_penalty: float = Field(default=5.0, description="[Legacy] Morning penalty stub")
    friday_penalty: float = Field(default=5.0, description="[Legacy] Friday penalty stub")
    monday_penalty: float = Field(default=5.0, description="[Legacy] Monday penalty stub")
    afternoon_penalty: float = Field(default=5.0, description="[Legacy] Afternoon penalty stub")


class PlanAnalysis(BaseModel):
    """Aggregated metadata and analysis for one schedule plan."""

    total_credits: int = Field(..., description="Sum of all course credits")
    school_days: int = Field(..., description="Number of days with at least one class")
    earliest_period: int = Field(
        ..., description="Earliest period number across the week"
    )
    score_breakdown: ScoreBreakdown
    reasons: list[str] = Field(
        default_factory=list, description="Natural language recommendation reasons"
    )


class Plan(BaseModel):
    """One complete ranked schedule recommendation."""

    id: str = Field(..., description="Plan identifier: plan_A, plan_B, plan_C")
    rank: int = Field(..., ge=1, le=3, description="Rank: 1 (best), 2, or 3")
    score: float = Field(..., description="Weighted total score (0-10)")
    label: str = Field(
        ..., description="Display label: 推荐方案 A / 备选方案 B / 备选方案 C"
    )
    courses: list[Course] = Field(..., description="Selected course sections")
    analysis: PlanAnalysis
    matched_strategies: list[str] = Field(
        default_factory=list,
        description="Strategy IDs that apply to this plan",
    )
    llm_review: Optional[dict] = Field(
        default=None,
        description="LLM evaluation (only when llm_evaluate=True)"
    )
