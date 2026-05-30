import { Brain } from "lucide-react";
import StrategyCard from "./StrategyCard";
import type { Strategy } from "@/types/strategy";

interface StrategySectionProps {
  strategies: Strategy[];
}

export default function StrategySection({ strategies }: StrategySectionProps) {
  if (strategies.length === 0) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Brain className="h-4 w-4 text-accent" />
        <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          AI 选课哲学 · 全部技巧
        </span>
        <span className="text-[10px] text-text-tertiary bg-surface-secondary rounded-full px-2 py-0.5">
          {strategies.length}条
        </span>
      </div>

      <div className="space-y-2">
        {strategies.map((strategy) => (
          <StrategyCard key={strategy.id} strategy={strategy} />
        ))}
      </div>
    </div>
  );
}
