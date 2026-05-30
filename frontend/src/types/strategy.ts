// Mirrors backend models/strategy.py Strategy
export interface Strategy {
  id: string;
  category: string;
  title: string;
  summary: string;
  detail: string;
  icon: string;
  example?: Record<string, unknown>;
  applicable_scenarios: string[];
  difficulty: string;
  trigger_condition?: Record<string, unknown>;
  ai_prompt_fragment?: string;
}

export interface StrategyListResponse {
  strategies: Strategy[];
}
