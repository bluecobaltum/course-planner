import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
  CheckCircle,
  Clock,
  Hash,
  AlertCircle,
  RotateCcw,
  Zap,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import CourseRow from "@/components/CourseRow";
import { createCourse } from "@/api/schedule";
import type { ImportResult } from "@/types/schedule";

interface ImportResultPreviewProps {
  result: ImportResult;
  onRetry: () => void;
  onDone: () => void;
}

const METHOD_LABELS: Record<string, string> = {
  excel: "Excel 导入",
  text: "AI 文本解析",
  image: "图片识别",
};

const BENCHMARK = [
  { method: "Excel 导入", accuracy: "★★★★★", cost: "免费", speed: "最快", highlight: "excel" },
  { method: "AI 文本解析", accuracy: "★★★★☆", cost: "低", speed: "中等", highlight: "text" },
  { method: "图片识别", accuracy: "★★★☆☆", cost: "Demo", speed: "中等", highlight: "image" },
];

export default function ImportResultPreview({
  result,
  onRetry,
  onDone,
}: ImportResultPreviewProps) {
  const [importing, setImporting] = useState(false);
  const [imported, setImported] = useState(0);
  const [errors, setErrors] = useState<string[]>([]);
  const [removedIndices, setRemovedIndices] = useState<Set<number>>(new Set());

  const visibleCourses = useMemo(
    () => result.courses.filter((_, i) => !removedIndices.has(i)),
    [result.courses, removedIndices]
  );

  const handleRemoveCourse = (idx: number) => {
    setRemovedIndices((prev) => new Set([...prev, idx]));
  };

  const handleConfirmImport = async () => {
    setImporting(true);
    setErrors([]);
    let count = 0;
    const errs: string[] = [];

    for (const course of visibleCourses) {
      try {
        await createCourse(course);
        count++;
      } catch (e) {
        errs.push(
          `${course.course_name}: ${e instanceof Error ? e.message : "导入失败"}`
        );
      }
    }

    setImported(count);
    setErrors(errs);
    setImporting(false);

    if (errs.length === 0) {
      setTimeout(onDone, 800);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5"
    >
      {/* ── Summary ── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="rounded-2xl border border-border/40 bg-paper/70 p-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent/10">
            <Zap className="h-5 w-5 text-accent" />
          </div>
          <div>
            <div className="text-xs text-text-tertiary">导入方式</div>
            <div className="text-sm font-semibold text-text-primary">
              {METHOD_LABELS[result.method] || result.method}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-border/40 bg-paper/70 p-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50">
            <Hash className="h-5 w-5 text-emerald-500" />
          </div>
          <div>
            <div className="text-xs text-text-tertiary">识别课程数</div>
            <div className="text-sm font-semibold text-text-primary">
              {visibleCourses.length} 门
              {removedIndices.size > 0 && (
                <span className="text-xs font-normal text-text-tertiary ml-1">
                  (已移除 {removedIndices.size} 门)
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-border/40 bg-paper/70 p-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50">
            <Clock className="h-5 w-5 text-amber-500" />
          </div>
          <div>
            <div className="text-xs text-text-tertiary">解析耗时</div>
            <div className="text-sm font-semibold text-text-primary">
              {result.stats.processing_time_ms.toFixed(0)} ms
            </div>
          </div>
        </div>
      </div>

      {/* ── Course List ── */}
      <div>
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
            解析结果
          </span>
          {removedIndices.size > 0 && (
            <button
              onClick={() => setRemovedIndices(new Set())}
              className="text-[11px] text-accent hover:text-accent-dark transition-colors cursor-pointer"
            >
              恢复全部
            </button>
          )}
        </div>
        <div className="mt-2 space-y-1.5">
          {visibleCourses.map((course, i) => {
            const origIdx = result.courses.indexOf(course);
            return (
              <div key={`${course.section_id}-${origIdx}`} className="flex items-center gap-1.5 group">
                <div className="flex-1">
                  <CourseRow course={course} />
                </div>
                <button
                  onClick={() => handleRemoveCourse(origIdx)}
                  className="flex-shrink-0 h-7 w-7 flex items-center justify-center rounded-lg text-text-tertiary hover:text-danger hover:bg-red-50 transition-colors cursor-pointer opacity-0 group-hover:opacity-100"
                  title="移除此课程"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Benchmark Comparison ── */}
      <div>
        <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          导入策略比较
        </span>
        <div className="mt-2 rounded-2xl border border-border/40 bg-paper/50 overflow-hidden">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border/30 bg-surface-secondary/50">
                <th className="text-left px-4 py-2.5 font-medium text-text-secondary">方式</th>
                <th className="text-center px-4 py-2.5 font-medium text-text-secondary">准确率</th>
                <th className="text-center px-4 py-2.5 font-medium text-text-secondary">费用</th>
                <th className="text-center px-4 py-2.5 font-medium text-text-secondary">速度</th>
              </tr>
            </thead>
            <tbody>
              {BENCHMARK.map((row) => (
                <tr
                  key={row.method}
                  className={`border-b border-border/20 last:border-0 ${
                    row.highlight === result.method
                      ? "bg-accent/5 font-medium"
                      : ""
                  }`}
                >
                  <td className="px-4 py-2.5 text-text-primary">
                    {row.highlight === result.method && (
                      <span className="inline-block w-1.5 h-1.5 rounded-full bg-accent mr-1.5 align-middle" />
                    )}
                    {row.method}
                  </td>
                  <td className="text-center px-4 py-2.5 text-amber-500">
                    {row.accuracy}
                  </td>
                  <td className="text-center px-4 py-2.5 text-text-secondary">
                    {row.cost}
                  </td>
                  <td className="text-center px-4 py-2.5 text-text-secondary">
                    {row.speed}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Import Status ── */}
      {importing && (
        <div className="text-center text-sm text-text-secondary py-2">
          正在导入课程... {imported}/{visibleCourses.length}
        </div>
      )}

      {imported > 0 && !importing && errors.length === 0 && (
        <div className="flex items-center gap-2 rounded-xl bg-emerald-50 border border-emerald-200 px-4 py-3 text-sm text-emerald-700">
          <CheckCircle className="h-4 w-4" />
          成功导入 {imported} 门课程
        </div>
      )}

      {errors.length > 0 && (
        <div className="rounded-xl bg-red-50 border border-red-200 px-4 py-3 space-y-1">
          <div className="flex items-center gap-2 text-sm text-red-700">
            <AlertCircle className="h-4 w-4" />
            部分课程导入失败，成功 {imported}/{visibleCourses.length}
          </div>
          {errors.map((e, i) => (
            <div key={i} className="text-xs text-red-600 ml-6">
              {e}
            </div>
          ))}
        </div>
      )}

      {/* ── Actions ── */}
      <div className="flex gap-2 justify-end pt-2">
        <Button variant="secondary" size="lg" onClick={onRetry}>
          <RotateCcw className="h-4 w-4" />
          重新识别
        </Button>
        <Button
          variant="accent"
          size="lg"
          onClick={handleConfirmImport}
          disabled={importing}
        >
          <CheckCircle className="h-4 w-4" />
          确认导入
        </Button>
      </div>
    </motion.div>
  );
}
