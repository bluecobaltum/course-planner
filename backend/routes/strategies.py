"""GET /api/strategies endpoint.

Returns the strategy knowledge base, optionally filtered by scenario.
Strategies are the core differentiator — scientific course selection tips
presented as cards alongside schedule plans.
"""

from fastapi import APIRouter, Query

from engine.loader import load_strategies
from models.strategy import Strategy
from models.response import StrategyListResponse

router = APIRouter(prefix="/api", tags=["strategies"])


@router.get("/strategies", response_model=StrategyListResponse)
async def get_strategies(
    scenario: str | None = Query(
        default=None,
        description="Filter strategies applicable to this scenario",
        examples=["no_morning"],
    ),
) -> StrategyListResponse:
    """Get course selection strategy cards.

    Without the scenario parameter, returns ALL strategies.
    With a scenario parameter, filters to strategies whose
    applicable_scenarios includes the given scenario or "all".

    Args:
        scenario: Optional scenario ID to filter by.

    Returns:
        StrategyListResponse with matching strategy cards.
    """
    raw_strategies = load_strategies()

    # Filter by scenario if provided
    if scenario:
        raw_strategies = [
            s
            for s in raw_strategies
            if scenario in s.get("applicable_scenarios", [])
            or "all" in s.get("applicable_scenarios", [])
        ]

    # Convert to Pydantic models
    strategies = [Strategy(**s) for s in raw_strategies]

    return StrategyListResponse(strategies=strategies)
