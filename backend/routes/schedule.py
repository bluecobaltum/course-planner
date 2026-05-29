"""POST /api/generate_schedule endpoint.

Receives a scenario + easy_count, generates top-3 schedule plans,
and returns them with full scoring analysis and strategy matches.
"""

from fastapi import APIRouter

from engine import generate_plans
from models.course import Course
from models.schedule import ScoreBreakdown, PlanAnalysis, Plan
from models.response import GenerateRequest, GenerateResponse

router = APIRouter(prefix="/api", tags=["schedule"])


@router.post("/generate_schedule", response_model=GenerateResponse)
async def generate_schedule(request: GenerateRequest) -> GenerateResponse:
    """Generate top-3 optimized course schedule plans.

    The request's scenario field is validated by Pydantic before this handler
    runs, so we know it's a valid scenario ID.

    Args:
        request: GenerateRequest with scenario (validated) and easy_count (0-5).

    Returns:
        GenerateResponse with 0-3 Plan objects. An empty plans list
        means no feasible schedule exists with the current constraints
        and data (not an error — the frontend should show a retry suggestion).
    """
    raw_plans = generate_plans(
        scenario=request.scenario,
        easy_count=request.easy_count,
    )

    # Convert raw plan dicts to Pydantic Plan models
    plans: list[Plan] = []
    for raw in raw_plans:
        # Convert course dicts to Course models
        courses = [Course(**c) for c in raw["courses"]]

        # Build nested models
        breakdown = ScoreBreakdown(**raw["analysis"]["score_breakdown"])
        analysis = PlanAnalysis(
            total_credits=raw["analysis"]["total_credits"],
            school_days=raw["analysis"]["school_days"],
            earliest_period=raw["analysis"]["earliest_period"],
            score_breakdown=breakdown,
            reasons=raw["analysis"]["reasons"],
        )

        plan = Plan(
            id=raw["id"],
            rank=raw["rank"],
            score=raw["score"],
            label=raw["label"],
            courses=courses,
            analysis=analysis,
            matched_strategies=raw["matched_strategies"],
        )
        plans.append(plan)

    return GenerateResponse(scenario=request.scenario, plans=plans)
