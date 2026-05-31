"""
Scheduler factory — selects between LLM, OR-Tools and Legacy scheduler.

Controlled by SCHEDULER environment variable:
  SCHEDULER=llm      → LLMScheduler (AI picks courses, code validates)
  SCHEDULER=ortools  → ORToolsScheduler (CP-SAT optimization)
  SCHEDULER=legacy   → LegacyScheduler (brute-force fallback)
  SCHEDULER=auto     → ORToolsScheduler, falls back to Legacy on ImportError
"""

import os
from schedulers.base import BaseScheduler


def get_scheduler() -> BaseScheduler:
    """Create and return the configured scheduler instance."""
    mode = os.environ.get("SCHEDULER", "legacy").lower()

    if mode == "llm":
        from schedulers.llm_scheduler import LLMScheduler
        return LLMScheduler()

    if mode == "legacy":
        from schedulers.legacy_scheduler import LegacyScheduler
        return LegacyScheduler()

    if mode in ("ortools", "auto", ""):
        try:
            from schedulers.ortools_scheduler import ORToolsScheduler
            import ortools.sat.python.cp_model  # noqa: F401
            return ORToolsScheduler()
        except Exception as e:
            if mode == "ortools":
                raise RuntimeError(
                    f"OR-Tools failed to initialize: {e}. "
                    "Set SCHEDULER=legacy to use the fallback engine."
                )
            from schedulers.legacy_scheduler import LegacyScheduler
            return LegacyScheduler()

    raise ValueError(f"Unknown SCHEDULER value: {mode}. Use: llm | ortools | legacy | auto")
