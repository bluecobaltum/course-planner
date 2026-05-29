"""Schedule output data models.

These models define the shape of a generated schedule plan —
the scored, analyzed output that the frontend receives.
"""

from pydantic import BaseModel, Field

from models.course import Course


class ScoreBreakdown(BaseModel):
    """The 8 sub-scores that make up a plan's weighted total.

    All scores are in range [1.0, 10.0]. Higher is always better.
    Penalty dimensions produce high scores when the penalty is NOT triggered
    (e.g., no morning classes → morning_penalty = 10.0).
    """

    gpa_score: float = Field(..., description="Teacher rating avg × 2 (2.0-10.0)")
    compact_score: float = Field(..., description="Schedule compactness (1.0-10.0)")
    stress_score: float = Field(..., description="Credit load stress (1.0-10.0)")
    free_score: float = Field(..., description="Free half-day count (0-10)")
    morning_penalty: float = Field(
        ..., description="Morning class penalty (10.0 = no mornings, 1.0 = many)"
    )
    friday_penalty: float = Field(
        ..., description="Friday class penalty (10.0 = free Friday, 3.0 = has class)"
    )
    monday_penalty: float = Field(
        ..., description="Monday class penalty (10.0 = free Monday, 3.0 = has class)"
    )
    afternoon_penalty: float = Field(
        ..., description="Afternoon class penalty (10.0 = no afternoon, 1.0 = many)"
    )


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
