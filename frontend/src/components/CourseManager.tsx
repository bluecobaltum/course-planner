import { useState, useEffect, useCallback } from "react";
import { Plus, FileText } from "lucide-react";
import { Button } from "@/components/ui/Button";
import CourseList from "@/components/CourseList";
import CourseEditor from "@/components/CourseEditor";
import AIImport from "@/components/AIImport";
import {
  getCourses,
  createCourse,
  updateCourse,
  deleteCourse,
} from "@/api/schedule";
import type { Course } from "@/types/schedule";

export default function CourseManager() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Editor state
  const [editorOpen, setEditorOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);

  // Load courses
  const loadCourses = useCallback(async () => {
    try {
      setError(null);
      const data = await getCourses();
      setCourses(data);
    } catch {
      setError("无法加载课程数据，请确认后端已启动");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCourses();
  }, [loadCourses]);

  // Handlers
  const handleCreate = () => {
    setEditingCourse(null);
    setEditorOpen(true);
  };

  const handleEdit = (course: Course) => {
    setEditingCourse(course);
    setEditorOpen(true);
  };

  const handleSave = async (course: Course) => {
    try {
      if (editingCourse) {
        await updateCourse(editingCourse.section_id, course);
      } else {
        await createCourse(course);
      }
      setEditorOpen(false);
      setEditingCourse(null);
      await loadCourses();
    } catch (e) {
      alert(e instanceof Error ? e.message : "保存失败");
    }
  };

  const handleDelete = async (sectionId: string) => {
    try {
      await deleteCourse(sectionId);
      await loadCourses();
    } catch (e) {
      alert(e instanceof Error ? e.message : "删除失败");
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12 text-text-tertiary text-sm">
        加载课程数据中...
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-text-primary">
          📚 课程数据管理
        </h2>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={loadCourses}
            className="text-xs"
          >
            <FileText className="h-3.5 w-3.5" />
            刷新
          </Button>
          <Button
            size="sm"
            onClick={handleCreate}
            disabled={editorOpen}
          >
            <Plus className="h-3.5 w-3.5" />
            添加课程
          </Button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50/60 p-3 text-sm text-red-600">
          {error}
        </div>
      )}

      {/* AI Import placeholder */}
      <AIImport />

      {/* Course Editor (inline) */}
      {editorOpen && (
        <CourseEditor
          course={editingCourse}
          onSave={handleSave}
          onCancel={() => {
            setEditorOpen(false);
            setEditingCourse(null);
          }}
        />
      )}

      {/* Course List */}
      <CourseList
        courses={courses}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}
