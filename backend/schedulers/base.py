"""
Abstract base class for schedule generation engines.

All schedulers implement this interface so the API route can switch
between implementations without changing request/response handling.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseScheduler(ABC):
    """Unified interface for schedule plan generation.

    Each concrete implementation (LegacyScheduler, ORToolsScheduler)
    returns the same list-of-dicts shape used by the existing API.
    """

    @abstractmethod
    def generate_plans(
        self,
        scenario: str,
        easy_count: int = 1,
    ) -> list[dict[str, Any]]:
        """Generate top-3 schedule plans for a given scenario.

        Args:
            scenario: Scenario ID (e.g. "no_morning", "balanced").
            easy_count: Number of easy/elective courses to include.

        Returns:
            List of 0-3 plan dicts, each containing:
              - id, rank, score, label
              - courses (list of course dicts)
              - analysis (total_credits, school_days, earliest_period,
                score_breakdown, reasons)
              - matched_strategies (list of strategy IDs)
        """
        ...
