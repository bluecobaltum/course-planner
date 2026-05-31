"""
Schedulers package — schedule plan generation engines.

Provides:
  - BaseScheduler (ABC)
  - LegacyScheduler (wraps engine.orchestrator.generate_plans)
  - ORToolsScheduler (CP-SAT constraint optimization)
  - get_scheduler() factory (controlled by SCHEDULER env var)
"""
