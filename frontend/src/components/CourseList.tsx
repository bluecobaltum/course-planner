import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Edit2, Trash2, Clock, Star } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { formatPeriods } from "@/utils/format";
import type { Course } from "@/types/schedule";

interface CourseListProps {
  courses: Course[];
  onEdit: (course: Course) => void;
  onDelete: (sectionId: string) => void;
  onToggleRequired: (sectionId: string, required: boolean) => void;
}

export default function CourseList({
  courses,
  onEdit,
  onDelete,
  onToggleRequired,
}: CourseListProps) {
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const major = courses.filter((c) => c.course_type === "major");
  const easy = courses.filter((c) => c.course_type === "easy");

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-xs text-text-tertiary">
        <span>
          共 {courses.length} 门（{major.length} 专业课 + {easy.length} 水课）
        </span>
      </div>

      <div className="space-y-2">
        {courses.length === 0 && (
          <div className="text-center py-8 text-text-tertiary text-sm">
            还没有课程数据，点击上方按钮添加
          </div>
        )}

        <AnimatePresence>
          {courses.map((course) => (
            <motion.div
              key={course.section_id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, height: 0 }}
              className="flex items-center gap-3 rounded-xl border border-border/40 bg-paper/50 p-3 hover:border-accent/20 transition-colors group"
            >
              {/* Type dot */}
              <div
                className={`h-2.5 w-2.5 rounded-full flex-shrink-0 ${
                  course.course_type === "major" ? "bg-indigo-400" : "bg-emerald-400"
                }`}
              />

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-medium text-text-primary truncate">
                    {course.course_name}
                  </span>
                  <span className="text-[11px] font-mono text-text-tertiary">
                    {course.section_id}
                  </span>
                  <Badge
                    variant={
                      course.course_type === "major" ? "blue" : "green"
                    }
                    className="text-[10px] px-1.5 py-0"
                  >
                    {course.course_type === "major" ? "专业课" : "水课"}
                  </Badge>
                  <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                    {course.delivery_mode}
                  </Badge>
                  {course.required && (
                    <span className="text-[10px] font-semibold text-amber-600 bg-amber-50 border border-amber-200 rounded-full px-1.5 py-0">
                      必选
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 mt-0.5 text-[11px] text-text-tertiary">
                  {course.teacher ? (
                    <span>
                      {course.teacher.name} · {course.teacher.rating}分
                    </span>
                  ) : (
                    <span>教师待定</span>
                  )}
                  <span>·</span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatPeriods(course.schedule)}
                  </span>
                  <span>·</span>
                  <span>{course.credits}学分</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-0.5">
                {/* Star — always visible */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onToggleRequired(course.section_id, !course.required)}
                  className="h-8 w-8 p-0"
                  title={course.required ? "取消必选" : "设为必选"}
                >
                  <Star className={`h-3.5 w-3.5 ${course.required ? "fill-amber-400 text-amber-400" : "text-text-tertiary"}`} />
                </Button>

                {/* Edit/Delete — hover only */}
                <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEdit(course)}
                    className="h-8 w-8 p-0"
                  >
                    <Edit2 className="h-3.5 w-3.5" />
                  </Button>

                  {deleteConfirm === course.section_id ? (
                    <>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          onDelete(course.section_id);
                          setDeleteConfirm(null);
                        }}
                        className="h-7 text-[10px] px-2 text-red-500 hover:text-red-700 hover:bg-red-50"
                      >
                        确认
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setDeleteConfirm(null)}
                        className="h-7 text-[10px] px-2"
                      >
                        取消
                      </Button>
                    </>
                  ) : (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setDeleteConfirm(course.section_id)}
                      className="h-8 w-8 p-0 text-red-400 hover:text-red-600"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
