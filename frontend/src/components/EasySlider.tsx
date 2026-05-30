import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { EASY_MAX } from "@/constants/scenarios";

interface EasySliderProps {
  value: number;
  onChange: (v: number) => void;
}

export default function EasySlider({ value, onChange }: EasySliderProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          水课数量
        </span>
        <div className="h-px flex-1 bg-border/50" />
        <span className="text-sm font-medium text-accent tabular-nums">
          {value} 门
        </span>
      </div>

      <div className="flex items-center justify-center gap-1 py-2">
        {Array.from({ length: EASY_MAX + 1 }, (_, i) => (
          <motion.button
            key={i}
            whileTap={{ scale: 0.9 }}
            onClick={() => onChange(i)}
            className="flex items-center gap-1"
            aria-label={`${i} 门水课`}
          >
            {/* Dot */}
            <motion.div
              animate={{
                scale: i <= value ? 1 : 0.6,
                backgroundColor:
                  i <= value ? "rgb(99,102,241)" : "rgb(203,213,225)",
              }}
              className={cn(
                "h-5 w-5 rounded-full transition-shadow cursor-pointer",
                i <= value && "shadow-md shadow-accent/30"
              )}
            />

            {/* Connector line (except after last) */}
            {i < EASY_MAX && (
              <motion.div
                animate={{
                  backgroundColor:
                    i < value ? "rgb(99,102,241)" : "rgb(226,232,240)",
                }}
                className="h-0.5 w-8 rounded-full"
                style={{ backgroundColor: i < value ? "rgb(99,102,241)" : undefined }}
              />
            )}
          </motion.button>
        ))}
      </div>

      {/* Labels */}
      <div className="flex justify-between px-1">
        <span className="text-[10px] text-text-tertiary">纯必修</span>
        <span className="text-[10px] text-text-tertiary">全加水课</span>
      </div>
    </div>
  );
}
