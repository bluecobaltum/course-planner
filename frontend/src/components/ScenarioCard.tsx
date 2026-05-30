import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { ScenarioMeta } from "@/constants/scenarios";

interface ScenarioCardProps {
  scenario: ScenarioMeta;
  selected: boolean;
  onSelect: (id: string) => void;
}

export default function ScenarioCard({
  scenario,
  selected,
  onSelect,
}: ScenarioCardProps) {
  const Icon = scenario.icon;

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSelect(scenario.id)}
      className={cn(
        "relative flex flex-col items-start gap-3 rounded-2xl border p-5 text-left transition-all duration-300 cursor-pointer",
        selected
          ? "border-accent/60 bg-white/90 glow ring-1 ring-accent/20"
          : "border-border/60 bg-white/60 hover:border-accent/30 hover:bg-white/80 hover:shadow-md"
      )}
    >
      {/* Glow bar on top when selected */}
      {selected && (
        <motion.div
          layoutId="glowBar"
          className="absolute top-0 left-4 right-4 h-0.5 rounded-full bg-gradient-to-r from-accent via-accent-light to-accent"
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        />
      )}

      {/* Icon */}
      <div
        className={cn(
          "flex h-10 w-10 items-center justify-center rounded-xl transition-colors",
          selected
            ? "bg-accent/10 text-accent"
            : "bg-surface-secondary text-text-secondary"
        )}
      >
        <Icon className="h-5 w-5" />
      </div>

      {/* Title + Description */}
      <div className="flex flex-col gap-1">
        <span
          className={cn(
            "text-sm font-semibold",
            selected ? "text-accent" : "text-text-primary"
          )}
        >
          {scenario.title}
        </span>
        <span className="text-xs text-text-secondary leading-relaxed line-clamp-2">
          {scenario.description}
        </span>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1.5">
        {scenario.tags.map((tag) => (
          <span
            key={tag}
            className={cn(
              "inline-block rounded-full px-2 py-0.5 text-[10px] font-medium",
              selected
                ? "bg-accent/10 text-accent"
                : "bg-surface-secondary text-text-tertiary"
            )}
          >
            {tag}
          </span>
        ))}
      </div>

      {/* Weight preview */}
      <span className="text-[10px] text-text-tertiary mt-auto leading-tight">
        {scenario.weightPreview}
      </span>
    </motion.button>
  );
}
