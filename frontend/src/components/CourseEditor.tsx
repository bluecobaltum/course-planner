import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { X, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import type { Course, ScheduleSlot } from "@/types/schedule";

const EMPTY_SLOT: ScheduleSlot = { day: 1, start: 1, end: 2 };

const DAY_OPTIONS = [
  { v: 1, l: "周一" },
  { v: 2, l: "周二" },
  { v: 3, l: "周三" },
  { v: 4, l: "周四" },
  { v: 5, l: "周五" },
];

const TYPE_OPTIONS = [
  { v: "major", l: "专业课" },
  { v: "easy", l: "水课/选修" },
];

const MODE_OPTIONS = [
  { v: "线下传统", l: "线下传统" },
  { v: "线上网课", l: "线上网课" },
  { v: "线上线下混合", l: "线上线下混合" },
];

interface CourseEditorProps {
  course: Course | null; // null = create mode
  onSave: (course: Course) => void;
  onCancel: () => void;
}

export default function CourseEditor({
  course,
  onSave,
  onCancel,
}: CourseEditorProps) {
  const isEdit = course !== null;

  const [sectionId, setSectionId] = useState("");
  const [courseCode, setCourseCode] = useState("");
  const [courseName, setCourseName] = useState("");
  const [creditGroup, setCreditGroup] = useState("");
  const [credits, setCredits] = useState(3);
  const [teacherName, setTeacherName] = useState("");
  const [teacherRating, setTeacherRating] = useState(4.0);
  const [slots, setSlots] = useState<ScheduleSlot[]>([EMPTY_SLOT]);
  const [building, setBuilding] = useState("");
  const [floor, setFloor] = useState(1);
  const [room, setRoom] = useState("");
  const [courseType, setCourseType] = useState<"major" | "easy">("major");
  const [deliveryMode, setDeliveryMode] = useState<
    "线下传统" | "线上网课" | "线上线下混合"
  >("线下传统");

  useEffect(() => {
    if (course) {
      setSectionId(course.section_id);
      setCourseCode(course.course_code);
      setCourseName(course.course_name);
      setCreditGroup(course.credit_transfer_group);
      setCredits(course.credits);
      setTeacherName(course.teacher?.name ?? "");
      setTeacherRating(course.teacher?.rating ?? 4.0);
      setSlots(
        course.schedule.length > 0 ? [...course.schedule] : [EMPTY_SLOT]
      );
      setBuilding(course.location?.building ?? "");
      setFloor(course.location?.floor ?? 1);
      setRoom(course.location?.room ?? "");
      setCourseType(course.course_type);
      setDeliveryMode(course.delivery_mode);
    }
  }, [course]);

  const handleSave = () => {
    if (!sectionId.trim() || !courseCode.trim() || !courseName.trim()) return;

    const newCourse: Course = {
      section_id: sectionId.trim(),
      course_code: courseCode.trim(),
      course_name: courseName.trim(),
      credit_transfer_group:
        creditGroup.trim() || courseCode.trim(),
      credits,
      teacher: teacherName.trim()
        ? { name: teacherName.trim(), rating: teacherRating }
        : null,
      schedule:
        deliveryMode === "线上网课" && slots.every((s) => s.start === 1 && s.end === 2)
          ? []
          : slots.filter((s) => s.start > 0 && s.end >= s.start),
      location:
        building.trim() || room.trim()
          ? { building: building.trim() || "-", floor, room: room.trim() || "-" }
          : null,
      course_type: courseType,
      delivery_mode: deliveryMode,
      semester: "2025-2026-2",
    };

    onSave(newCourse);
  };

  const addSlot = () =>
    setSlots([...slots, { day: 1, start: 1, end: 2 }]);

  const removeSlot = (i: number) =>
    setSlots(slots.filter((_, idx) => idx !== i));

  const updateSlot = (i: number, f: Partial<ScheduleSlot>) =>
    setSlots(slots.map((s, idx) => (idx === i ? { ...s, ...f } : s)));

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-accent/30 bg-white/90 backdrop-blur p-6 space-y-5"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-text-primary">
          {isEdit ? "编辑课程" : "添加课程"}
        </h3>
        <Button variant="ghost" size="sm" onClick={onCancel}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Row 1: Basic Info */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <label className="space-y-1">
          <span className="text-[10px] text-text-tertiary">班号 *</span>
          <input
            value={sectionId}
            onChange={(e) => setSectionId(e.target.value)}
            placeholder="MATH101-01"
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          />
        </label>
        <label className="space-y-1">
          <span className="text-[10px] text-text-tertiary">课程代码 *</span>
          <input
            value={courseCode}
            onChange={(e) => setCourseCode(e.target.value)}
            placeholder="MATH101"
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          />
        </label>
        <label className="space-y-1 sm:col-span-2">
          <span className="text-[10px] text-text-tertiary">课程名称 *</span>
          <input
            value={courseName}
            onChange={(e) => setCourseName(e.target.value)}
            placeholder="高等数学A"
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          />
        </label>
      </div>

      {/* Row 2: Group + Credits + Type + Mode */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <label className="space-y-1">
          <span className="text-[10px] text-text-tertiary">学分互认组</span>
          <input
            value={creditGroup}
            onChange={(e) => setCreditGroup(e.target.value)}
            placeholder={courseCode || "同课程代码"}
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          />
        </label>
        <label className="space-y-1">
          <span className="text-[10px] text-text-tertiary">学分</span>
          <input
            type="number"
            min={1}
            max={10}
            value={credits}
            onChange={(e) => setCredits(Number(e.target.value) || 1)}
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          />
        </label>
        <label className="space-y-1">
          <span className="text-[10px] text-text-tertiary">课程类型</span>
          <select
            value={courseType}
            onChange={(e) =>
              setCourseType(e.target.value as "major" | "easy")
            }
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          >
            {TYPE_OPTIONS.map((o) => (
              <option key={o.v} value={o.v}>
                {o.l}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-1">
          <span className="text-[10px] text-text-tertiary">授课模式</span>
          <select
            value={deliveryMode}
            onChange={(e) =>
              setDeliveryMode(
                e.target.value as "线下传统" | "线上网课" | "线上线下混合"
              )
            }
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          >
            {MODE_OPTIONS.map((o) => (
              <option key={o.v} value={o.v}>
                {o.l}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* Row 3: Teacher */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <label className="space-y-1 sm:col-span-2">
          <span className="text-[10px] text-text-tertiary">教师姓名</span>
          <input
            value={teacherName}
            onChange={(e) => setTeacherName(e.target.value)}
            placeholder="留空表示教师待定"
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          />
        </label>
        <label className="space-y-1">
          <span className="text-[10px] text-text-tertiary">
            评教分数 (1-5)
          </span>
          <input
            type="number"
            min={1}
            max={5}
            step={0.1}
            value={teacherRating}
            onChange={(e) =>
              setTeacherRating(Math.min(5, Math.max(1, Number(e.target.value) || 4.0)))
            }
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          />
        </label>
      </div>

      {/* Row 4: Schedule Slots */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-text-tertiary">
            上课时间（线上异步课可留空）
          </span>
          <Button variant="ghost" size="sm" onClick={addSlot}>
            <Plus className="h-3.5 w-3.5" />
            加时段
          </Button>
        </div>
        {slots.map((slot, i) => (
          <div key={i} className="flex items-center gap-2">
            <select
              value={slot.day}
              onChange={(e) =>
                updateSlot(i, { day: Number(e.target.value) })
              }
              className="rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
            >
              {DAY_OPTIONS.map((d) => (
                <option key={d.v} value={d.v}>
                  {d.l}
                </option>
              ))}
            </select>
            <span className="text-xs text-text-tertiary">第</span>
            <input
              type="number"
              min={1}
              max={14}
              value={slot.start}
              onChange={(e) =>
                updateSlot(i, { start: Number(e.target.value) || 1 })
              }
              className="w-14 rounded-lg border border-border/60 px-2 py-2 text-sm text-center bg-white focus:outline-none focus:border-accent/50"
            />
            <span className="text-xs text-text-tertiary">-</span>
            <input
              type="number"
              min={1}
              max={14}
              value={slot.end}
              onChange={(e) =>
                updateSlot(i, { end: Number(e.target.value) || slot.start })
              }
              className="w-14 rounded-lg border border-border/60 px-2 py-2 text-sm text-center bg-white focus:outline-none focus:border-accent/50"
            />
            <span className="text-xs text-text-tertiary">节</span>
            {slots.length > 1 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeSlot(i)}
                className="h-8 w-8 p-0 text-red-400 hover:text-red-600"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>
        ))}
      </div>

      {/* Row 5: Location */}
      <div className="grid grid-cols-3 gap-3">
        <label className="space-y-1">
          <span className="text-[10px] text-text-tertiary">教学楼</span>
          <input
            value={building}
            onChange={(e) => setBuilding(e.target.value)}
            placeholder="汇文楼"
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          />
        </label>
        <label className="space-y-1">
          <span className="text-[10px] text-text-tertiary">楼层</span>
          <input
            type="number"
            min={0}
            value={floor}
            onChange={(e) => setFloor(Number(e.target.value) || 0)}
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          />
        </label>
        <label className="space-y-1">
          <span className="text-[10px] text-text-tertiary">教室</span>
          <input
            value={room}
            onChange={(e) => setRoom(e.target.value)}
            placeholder="301"
            className="w-full rounded-lg border border-border/60 px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent/50"
          />
        </label>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-2 pt-2">
        <Button variant="secondary" onClick={onCancel}>
          取消
        </Button>
        <Button
          variant="accent"
          onClick={handleSave}
          disabled={!sectionId.trim() || !courseCode.trim() || !courseName.trim()}
        >
          {isEdit ? "保存修改" : "添加课程"}
        </Button>
      </div>
    </motion.div>
  );
}
