import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";
import { ChevronDown } from "lucide-react";
import type { Course } from "@/types/schedule";

interface ScheduleGridProps {
  courses: Course[];
}

const CELL_HEIGHT = 28;
const PERIODS = 14;
const DAYS = [1, 2, 3, 4, 5] as const;
const DAY_LABELS = ["周一", "周二", "周三", "周四", "周五"];

interface Block {
  section_id: string;
  course_name: string;
  course_type: "major" | "easy";
  delivery_mode: string;
  day: number;
  start: number;
  end: number;
  color: string;
  isOnline: boolean;
}

const COURSE_COLORS = [
  "bg-amber-50 border-amber-200 text-amber-800",
  "bg-orange-50 border-orange-200 text-orange-800",
  "bg-yellow-50 border-yellow-200 text-yellow-800",
  "bg-lime-50 border-lime-200 text-lime-800",
  "bg-amber-50/70 border-amber-200/70 text-amber-700",
  "bg-orange-50/70 border-orange-200/70 text-orange-700",
  "bg-teal-50 border-teal-200 text-teal-800",
  "bg-emerald-50 border-emerald-200 text-emerald-800",
  "bg-yellow-50/70 border-yellow-200/70 text-yellow-700",
  "bg-lime-50/70 border-lime-200/70 text-lime-700",
];

export default function ScheduleGrid({ courses }: ScheduleGridProps) {
  const [showEvening, setShowEvening] = useState(false);
  const effectivePeriods = showEvening ? PERIODS : 10;

  const blocks = useMemo(() => {
    const result: Block[] = [];
    const colorMap = new Map<string, string>();
    let colorIdx = 0;

    for (const c of courses) {
      let color = colorMap.get(c.course_code);
      if (!color) {
        color = COURSE_COLORS[colorIdx % COURSE_COLORS.length];
        colorMap.set(c.course_code, color);
        colorIdx++;
      }

      for (const slot of c.schedule) {
        result.push({
          section_id: c.section_id,
          course_name: c.course_name,
          course_type: c.course_type,
          delivery_mode: c.delivery_mode,
          day: slot.day,
          start: slot.start,
          end: slot.end,
          color,
          isOnline: c.delivery_mode === "线上网课",
        });
      }
    }

    return result;
  }, [courses]);

  const gridHeight = effectivePeriods * CELL_HEIGHT;
  const hasEvening = blocks.some((b) => b.start > 10);

  return (
    <div>
      <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
        课表预览
      </span>

      <div className="mt-2 overflow-x-auto rounded-xl border border-border/40 bg-paper/50">
        <div className="flex" style={{ minWidth: 500 }}>
          {/* Period labels column */}
          <div className="flex-shrink-0 w-10">
            <div className="h-7" />
            {Array.from({ length: effectivePeriods }, (_, i) => (
              <div
                key={i}
                className="flex items-center justify-center text-[10px] text-text-tertiary font-mono"
                style={{ height: CELL_HEIGHT }}
              >
                {i + 1}
              </div>
            ))}
          </div>

          {/* Day columns */}
          {DAYS.map((day, dayIdx) => (
            <div key={day} className="flex-1 relative border-l border-border/30">
              <div
                className={cn(
                  "flex items-center justify-center text-[11px] font-medium h-7 border-b border-border/30",
                  day === 5 && "text-orange-500"
                )}
              >
                {DAY_LABELS[dayIdx]}
              </div>

              <div className="relative" style={{ height: gridHeight }}>
                {Array.from({ length: effectivePeriods + 1 }, (_, i) => (
                  <div
                    key={i}
                    className="absolute left-0 right-0 border-t border-border/20"
                    style={{ top: i * CELL_HEIGHT }}
                  />
                ))}

                <div
                  className="absolute left-0 right-0 border-t-2 border-dashed border-accent/20"
                  style={{ top: 5 * CELL_HEIGHT }}
                />

                {blocks
                  .filter((b) => b.day === day && (showEvening || b.start <= 10))
                  .map((block) => {
                    const top = (block.start - 1) * CELL_HEIGHT;
                    const height = (block.end - block.start + 1) * CELL_HEIGHT;

                    return (
                      <div
                        key={`${block.section_id}-${block.day}-${block.start}`}
                        className={cn(
                          "absolute left-0.5 right-0.5 rounded-md border px-1.5 py-0.5 overflow-hidden transition-transform hover:scale-[1.03] hover:z-10 hover:shadow-md cursor-default",
                          block.color,
                          block.isOnline && "border-dashed opacity-80"
                        )}
                        style={{ top, height: Math.max(height, CELL_HEIGHT) }}
                        title={`${block.course_name} (${block.start}-${block.end}节)`}
                      >
                        <div className="text-[9px] font-semibold leading-tight truncate">
                          {block.course_name}
                        </div>
                        {height >= CELL_HEIGHT * 2 && (
                          <div className="text-[8px] leading-tight opacity-70">
                            {block.start}-{block.end}节
                          </div>
                        )}
                      </div>
                    );
                  })}
              </div>
            </div>
          ))}
        </div>

        {hasEvening && (
          <button
            onClick={() => setShowEvening(!showEvening)}
            className="flex items-center gap-1.5 w-full justify-center py-2 text-[11px] font-medium text-text-tertiary hover:text-accent transition-colors cursor-pointer border-t border-border/20"
          >
            <ChevronDown
              className={`h-3.5 w-3.5 transition-transform ${showEvening ? "rotate-180" : ""}`}
            />
            {showEvening ? "收起晚间课程 (11-14节)" : "展开晚间课程 (11-14节)"}
          </button>
        )}
      </div>
    </div>
  );
}
