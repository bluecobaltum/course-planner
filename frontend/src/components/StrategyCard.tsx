import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/Badge";
import type { Strategy } from "@/types/strategy";

interface StrategyCardProps {
  strategy: Strategy;
}

export default function StrategyCard({ strategy }: StrategyCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      layout
      className="rounded-2xl border border-border/50 bg-white/60 backdrop-blur-sm hover:border-accent/20 transition-colors overflow-hidden"
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-4 p-5 text-left cursor-pointer"
      >
        {/* Icon */}
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent/5 text-xl flex-shrink-0">
          {strategy.icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold text-text-primary">
              {strategy.title}
            </span>
            <Badge variant="secondary" className="text-[10px]">
              {strategy.category}
            </Badge>
            <Badge variant="secondary" className="text-[10px]">
              {strategy.difficulty}
            </Badge>
          </div>
          <p className="text-xs text-text-secondary mt-1 line-clamp-1">
            {strategy.summary}
          </p>
        </div>

        {/* Chevron */}
        <motion.div
          animate={{ rotate: expanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="flex-shrink-0 text-text-tertiary"
        >
          <ChevronDown className="h-5 w-5" />
        </motion.div>
      </button>

      {/* Expanded detail */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 pt-0">
              <div className="rounded-xl bg-surface-secondary/50 p-4 border border-border/30">
                <p className="text-sm text-text-secondary leading-relaxed">
                  {strategy.detail}
                </p>
                {strategy.example && (
                  <div className="mt-3 pt-3 border-t border-border/30">
                    <span className="text-[10px] font-semibold uppercase text-text-tertiary">
                      实际案例
                    </span>
                    <pre className="mt-1 text-xs text-text-secondary whitespace-pre-wrap font-sans">
                      {JSON.stringify(strategy.example, null, 2)}
                    </pre>
                  </div>
                )}
              </div>

              {/* Applicable scenarios */}
              <div className="flex flex-wrap gap-1.5 mt-3">
                {strategy.applicable_scenarios.map((s) => (
                  <Badge
                    key={s}
                    variant={s === "all" ? "purple" : "secondary"}
                    className="text-[10px]"
                  >
                    {s === "all" ? "全部场景" : s}
                  </Badge>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
