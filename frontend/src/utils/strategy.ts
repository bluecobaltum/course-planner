import type { Strategy } from "@/types/strategy";

export function joinStrategies(
  ids: string[],
  allStrategies: Strategy[]
): Strategy[] {
  const map = new Map(allStrategies.map((s) => [s.id, s]));
  return ids.map((id) => map.get(id)).filter((s): s is Strategy => s != null);
}

export function filterStrategies(
  strategies: Strategy[],
  scenario?: string
): Strategy[] {
  if (!scenario) return strategies;
  return strategies.filter(
    (s) =>
      s.applicable_scenarios.includes(scenario) ||
      s.applicable_scenarios.includes("all")
  );
}
