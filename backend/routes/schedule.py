"""POST /api/generate_schedule endpoint.

Receives a scenario + easy_count, generates top-3 schedule plans,
and returns them with full scoring analysis and strategy matches.
"""

from fastapi import APIRouter

from models.course import Course
from models.schedule import ScoreBreakdown, PlanAnalysis, Plan
from models.response import GenerateRequest, GenerateResponse
from schedulers.scheduler_factory import get_scheduler
from services.plan_evaluator import evaluate_plan

router = APIRouter(prefix="/api", tags=["schedule"])

# Default scheduler (OR-Tools or Legacy via env var)
_default_scheduler = get_scheduler()


@router.post("/generate_schedule", response_model=GenerateResponse)
async def generate_schedule(request: GenerateRequest) -> GenerateResponse:
    """Generate top-3 optimized course schedule plans."""

    model_override = request.llm_model.strip() if request.llm_model else ""
    custom_prompt = request.llm_prompt.strip() if request.llm_prompt else ""

    # If llm_evaluate + model specified → use LLMScheduler
    if request.llm_evaluate and request.llm_schedule:
        from schedulers.llm_scheduler import LLMScheduler
        llm = LLMScheduler()
        raw_plans = llm.generate_plans(
            scenario=request.scenario,
            easy_count=request.easy_count,
            model_override=model_override,
            custom_prompt=custom_prompt,
        )
    else:
        raw_plans = _default_scheduler.generate_plans(
            scenario=request.scenario,
            easy_count=request.easy_count,
        )

        # If default is LLM and returned empty, fall back to OR-Tools
        if not raw_plans:
            try:
                from schedulers.ortools_scheduler import ORToolsScheduler
                ortools = ORToolsScheduler()
                raw_plans = ortools.generate_plans(
                    scenario=request.scenario,
                    easy_count=request.easy_count,
                )
            except Exception:
                pass

    # Optional LLM evaluation of the top plan
    if request.llm_evaluate and raw_plans:
        review = evaluate_plan(raw_plans[0], model_override)
        if review:
            raw_plans[0]["llm_review"] = review

    # Convert raw plan dicts to Pydantic Plan models
    plans: list[Plan] = []
    for raw in raw_plans:
        courses = [Course(**c) for c in raw["courses"]]

        breakdown = ScoreBreakdown(**raw["analysis"]["score_breakdown"])
        analysis = PlanAnalysis(
            total_credits=raw["analysis"]["total_credits"],
            school_days=raw["analysis"]["school_days"],
            earliest_period=raw["analysis"]["earliest_period"],
            score_breakdown=breakdown,
            reasons=raw["analysis"]["reasons"],
        )

        plan_kwargs: dict = {
            "id": raw["id"],
            "rank": raw["rank"],
            "score": raw["score"],
            "label": raw["label"],
            "courses": courses,
            "analysis": analysis,
            "matched_strategies": raw["matched_strategies"],
        }
        if raw.get("llm_review"):
            plan_kwargs["llm_review"] = raw["llm_review"]

        plan = Plan(**plan_kwargs)
        plans.append(plan)

    return GenerateResponse(scenario=request.scenario, plans=plans)
