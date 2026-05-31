"""
LegacyScheduler — wraps the existing engine.orchestrator.generate_plans.

No algorithm changes. Pure adapter pattern. Serves as the fallback when
OR-Tools is unavailable or SCHEDULER=legacy is set.
"""

from typing import Any

from engine.orchestrator import generate_plans as _legacy_generate
from schedulers.base import BaseScheduler


class LegacyScheduler(BaseScheduler):
    """Thin wrapper around engine.orchestrator.generate_plans.

    Preserves all existing logic: grouping → cartesian product →
    conflict pruning → easy fill → scoring → dedup → top-3.
    """

    def generate_plans(
        self,
        scenario: str,
        easy_count: int = 1,
    ) -> list[dict[str, Any]]:
        return _legacy_generate(scenario=scenario, easy_count=easy_count)
