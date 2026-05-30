import { cn } from "@/lib/utils";

interface ScoreBarProps {
  label: string;
  value: number;
  max?: number;
}

function scoreColor(v: number): string {
  if (v >= 8) return "bg-emerald-400";
  if (v >= 6) return "bg-amber-400";
  if (v >= 4) return "bg-orange-400";
  return "bg-red-400";
}

export default function ScoreBar({ label, value, max = 10 }: ScoreBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className="flex items-center gap-2">
      <span className="w-20 text-xs text-text-secondary flex-shrink-0">
        {label}
      </span>
      <div className="flex-1 h-2 rounded-full bg-border/40 overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all duration-700", scoreColor(value))}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-8 text-right text-xs font-mono font-medium text-text-primary">
        {value.toFixed(1)}
      </span>
    </div>
  );
}
