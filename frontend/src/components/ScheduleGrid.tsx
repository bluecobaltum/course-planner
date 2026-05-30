import { useMemo } from "react";
import { cn } from "@/lib/utils";
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
  "bg-indigo-100 border-indigo-300 text-indigo-800",
  "bg-violet-100 border-violet-300 text-violet-800",
  "bg-sky-100 border-sky-300 text-sky-800",
  "bg-blue-100 border-blue-300 text-blue-800",
  "bg-purple-100 border-purple-300 text-purple-800",
  "bg-rose-100 border-rose-300 text-rose-800",
  "bg-teal-100 border-teal-300 text-teal-800",
  "bg-amber-100 border-amber-300 text-amber-800",
  "bg-emerald-100 border-emerald-300 text-emerald-800",
  "bg-cyan-100 border-cyan-300 text-cyan-800",
];

export default function ScheduleGrid({ courses }: ScheduleGridProps) {
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

  const gridHeight = PERIODS * CELL_HEIGHT;

  return (
    <div>
      <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
        课表预览
      </span>

      <div className="mt-2 overflow-x-auto rounded-xl border border-border/40 bg-white/50">
        <div className="flex" style={{ minWidth: 500 }}>
          {/* Period labels column */}
          <div className="flex-shrink-0 w-10">
            {/* Header spacer */}
            <div className="h-7" />
            {Array.from({ length: PERIODS }, (_, i) => (
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
              {/* Day header */}
              <div
                className={cn(
                  "flex items-center justify-center text-[11px] font-medium h-7 border-b border-border/30",
                  day === 5 && "text-orange-500"
                )}
              >
                {DAY_LABELS[dayIdx]}
              </div>

              {/* Grid container */}
              <div className="relative" style={{ height: gridHeight }}>
                {/* Period grid lines */}
                {Array.from({ length: PERIODS + 1 }, (_, i) => (
                  <div
                    key={i}
                    className="absolute left-0 right-0 border-t border-border/20"
                    style={{ top: i * CELL_HEIGHT }}
                  />
                ))}

                {/* Morning divider */}
                <div
                  className="absolute left-0 right-0 border-t-2 border-dashed border-amber-200/50"
                  style={{ top: 5 * CELL_HEIGHT }}
                />

                {/* Course blocks */}
                {blocks
                  .filter((b) => b.day === day)
                  .map((block, idx) => {
                    const top = (block.start - 1) * CELL_HEIGHT;
                    const height =
                      (block.end - block.start + 1) * CELL_HEIGHT;

                    return (
                      <div
                        key={`${block.section_id}-${idx}`}
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
      </div>
    </div>
  );
}
