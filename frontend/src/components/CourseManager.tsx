import { useState, useEffect, useCallback } from "react";
import { Plus, FileText, Trash2, Save } from "lucide-react";
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
  const [deleteAllConfirm, setDeleteAllConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

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

  const handleDeleteAll = async () => {
    setDeleting(true);
    for (const c of courses) {
      try { await deleteCourse(c.section_id); } catch { /* continue */ }
    }
    setDeleting(false);
    setDeleteAllConfirm(false);
    await loadCourses();
  };

  const handleToggleRequired = async (sectionId: string, required: boolean) => {
    const course = courses.find((c) => c.section_id === sectionId);
    if (!course) return;
    try {
      await updateCourse(sectionId, { ...course, required });
      await loadCourses();
    } catch { /* ignore */ }
  };
  const handleDelete = async (sectionId: string) => {
    try {
      await deleteCourse(sectionId);
      await loadCourses();
    } catch (e) {
      alert(e instanceof Error ? e.message : "删除失败");
    }
  };

  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(courses, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "courses.json";
    a.click();
    URL.revokeObjectURL(url);
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
          {courses.length > 0 && (
            deleteAllConfirm ? (
              <>
                <span className="text-xs text-danger font-medium">确认删除全部 {courses.length} 门课程？</span>
                <Button variant="ghost" size="sm" onClick={() => setDeleteAllConfirm(false)} disabled={deleting} className="text-xs">取消</Button>
                <Button variant="ghost" size="sm" onClick={handleDeleteAll} disabled={deleting} className="text-xs text-danger hover:text-danger hover:bg-red-50">
                  {deleting ? "删除中..." : "确认全部删除"}
                </Button>
              </>
            ) : (
              <Button variant="ghost" size="sm" onClick={() => setDeleteAllConfirm(true)} className="text-xs text-text-tertiary hover:text-danger">
                <Trash2 className="h-3.5 w-3.5" />
                全部删除
              </Button>
            )
          )}
          {courses.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleExportJSON}
              className="text-xs text-text-tertiary hover:text-accent"
              title="导出为 courses.json"
            >
              <Save className="h-3.5 w-3.5" />
              导出
            </Button>
          )}
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
        onToggleRequired={handleToggleRequired}
      />
    </div>
  );
}
