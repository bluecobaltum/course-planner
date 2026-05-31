import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/Badge";
import { formatPeriods, ratingStars, deliveryVariant } from "@/utils/format";
import type { Course } from "@/types/schedule";

interface CourseRowProps {
  course: Course;
}

export default function CourseRow({ course }: CourseRowProps) {
  const isMajor = course.course_type === "major";
  const isOnline = course.delivery_mode === "线上网课";
  const rating = course.teacher?.rating;

  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors",
        isMajor
          ? "bg-amber-50/50 border border-amber-100/50"
          : "bg-lime-50/50 border border-lime-100/50",
        isOnline && "border-dashed opacity-85"
      )}
    >
      {/* Course type indicator */}
      <div
        className={cn(
          "h-2 w-2 rounded-full flex-shrink-0",
          isMajor ? "bg-amber-400" : "bg-lime-400"
        )}
      />

      {/* Course body */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-text-primary truncate">
            {course.course_name}
          </span>
          <Badge
            variant={deliveryVariant(course.delivery_mode)}
            className="text-[10px] px-1.5 py-0 shrink-0"
          >
            {course.delivery_mode}
          </Badge>
          {course.required && (
            <span className="text-[10px] font-semibold text-amber-600 bg-amber-50 border border-amber-200 rounded-full px-1.5 py-0 shrink-0">
              必选
            </span>
          )}
        </div>

        <div className="flex items-center gap-3 mt-0.5 text-xs text-text-tertiary">
          {/* Teacher + rating */}
          {course.teacher ? (
            <span className="flex items-center gap-1">
              <span>{course.teacher.name}</span>
              {rating != null && (
                <span className="font-medium text-amber-500">
                  {ratingStars(rating)}
                  <span className="ml-0.5 text-text-tertiary">{rating}</span>
                </span>
              )}
            </span>
          ) : (
            <span>教师待定</span>
          )}

          {/* Time */}
          <span className="truncate">{formatPeriods(course.schedule)}</span>
        </div>
      </div>

      {/* Credits badge */}
      <span className="text-xs font-medium text-text-tertiary bg-paper/60 rounded-lg px-2 py-1 shrink-0 border border-border/40">
        {course.credits}学分
      </span>
    </div>
  );
}
