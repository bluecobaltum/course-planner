import { SCENARIOS } from "@/constants/scenarios";
import ScenarioCard from "./ScenarioCard";

interface ScenarioSelectorProps {
  selected: string;
  onSelect: (id: string) => void;
}

export default function ScenarioSelector({
  selected,
  onSelect,
}: ScenarioSelectorProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          选择你的大学生活偏好
        </span>
        <div className="h-px flex-1 bg-border/50" />
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {SCENARIOS.map((scenario) => (
          <ScenarioCard
            key={scenario.id}
            scenario={scenario}
            selected={selected === scenario.id}
            onSelect={onSelect}
          />
        ))}
      </div>
    </div>
  );
}
