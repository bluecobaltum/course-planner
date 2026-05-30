import { motion } from "framer-motion";
import { Sparkles, Upload, FileText } from "lucide-react";

export default function AIImport() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-2xl border-2 border-dashed border-amber-200/60 bg-gradient-to-br from-amber-50/30 to-amber-100/20 p-6 text-center"
    >
      <div className="flex justify-center mb-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-accent/10">
          <Sparkles className="h-8 w-8 text-accent" />
        </div>
      </div>

      <h3 className="text-base font-semibold text-text-primary mb-2">
        AI 智能导入课程数据
      </h3>
      <p className="text-sm text-text-secondary max-w-md mx-auto mb-5">
        上传教务系统 Excel / 截图 / 课程表图片，AI 自动识别并转换为课表数据
      </p>

      <div className="flex items-center justify-center gap-3 flex-wrap">
        <button
          disabled
          className="flex items-center gap-2 rounded-xl border border-border/40 bg-paper/60 px-4 py-2.5 text-sm font-medium text-text-tertiary cursor-not-allowed"
        >
          <Upload className="h-4 w-4" />
          上传 Excel
        </button>
        <button
          disabled
          className="flex items-center gap-2 rounded-xl border border-border/40 bg-paper/60 px-4 py-2.5 text-sm font-medium text-text-tertiary cursor-not-allowed"
        >
          <FileText className="h-4 w-4" />
          上传截图
        </button>
      </div>

      <p className="text-[11px] text-text-tertiary mt-4">
        🚧 此功能正在开发中，敬请期待
      </p>
    </motion.div>
  );
}
