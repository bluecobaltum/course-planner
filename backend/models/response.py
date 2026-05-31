"""API request/response models.

These define the IO contract between frontend and backend.
Pydantic handles validation at the boundary — bad data never reaches the engine.
"""

from pydantic import BaseModel, Field, field_validator

from models.schedule import Plan
from models.strategy import Strategy
from config.scenarios import SCENARIO_WEIGHTS

# ── Request Models ──────────────────────────────────────────


class GenerateRequest(BaseModel):
    """Request body for POST /generate_schedule."""

    scenario: str = Field(
        ...,
        description="Scenario ID, e.g. 'no_morning', 'gpa_focus'",
        examples=["no_morning"],
    )
    easy_count: int = Field(
        default=1,
        ge=0,
        le=5,
        description="Number of easy/elective course groups to include (0-5)",
        examples=[1],
    )
    llm_evaluate: bool = Field(
        default=False,
        description="If True, use LLM to select courses and evaluate the plan",
    )
    llm_schedule: bool = Field(
        default=False,
        description="If True, use LLM to pick the course combination (not OR-Tools)",
    )
    llm_model: str = Field(
        default="",
        description="Override LLM model (defaults to LLM_EVAL_MODEL env var)",
    )
    llm_prompt: str = Field(
        default="",
        description="Custom user prompt for LLM-based course selection",
    )

    @field_validator("scenario")
    @classmethod
    def scenario_must_be_valid(cls, v: str) -> str:
        """Validate scenario against the known list. Raises ValueError with hints."""
        if v not in SCENARIO_WEIGHTS:
            valid = ", ".join(sorted(SCENARIO_WEIGHTS.keys()))
            raise ValueError(
                f"Unknown scenario '{v}'. Valid options: {valid}"
            )
        return v


# ── Response Models ─────────────────────────────────────────


class GenerateResponse(BaseModel):
    """Response body for POST /generate_schedule.

    Returns 0-3 ranked plans. An empty plans list means no feasible
    schedule could be found with the current constraints and data.
    """

    scenario: str
    plans: list[Plan] = Field(
        default_factory=list,
        description="Top-3 ranked plans (empty if no feasible schedule)",
    )


class StrategyListResponse(BaseModel):
    """Response body for GET /strategies."""

    strategies: list[Strategy] = Field(
        default_factory=list,
        description="All matching strategy cards",
    )


class ErrorResponse(BaseModel):
    """Standard error response for all API errors."""

    error: str = Field(
        ...,
        description="Machine-readable error code, e.g. INVALID_SCENARIO",
        examples=["INVALID_SCENARIO"],
    )
    detail: str = Field(
        ...,
        description="Technical error description for debugging",
    )
    message: str = Field(
        ...,
        description="User-facing error message (Chinese)",
        examples=["请选择一个有效的选课方案"],
    )
