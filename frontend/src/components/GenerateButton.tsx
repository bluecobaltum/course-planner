import { motion } from "framer-motion";
import { Sparkles, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface GenerateButtonProps {
  loading: boolean;
  disabled: boolean;
  onClick: () => void;
}

export default function GenerateButton({
  loading,
  disabled,
  onClick,
}: GenerateButtonProps) {
  return (
    <motion.button
      whileHover={!loading && !disabled ? { scale: 1.03 } : undefined}
      whileTap={!loading && !disabled ? { scale: 0.97 } : undefined}
      onClick={onClick}
      disabled={loading || disabled}
      className={cn(
        "relative mx-auto flex items-center justify-center gap-3 overflow-hidden rounded-2xl px-10 py-5 text-lg font-semibold transition-all duration-300",
        loading || disabled
          ? "cursor-not-allowed bg-surface-secondary text-text-tertiary"
          : "bg-gradient-to-r from-accent via-accent-light to-accent text-white shadow-lg hover:shadow-xl cursor-pointer"
      )}
    >
      {/* Shimmer effect */}
      {!loading && !disabled && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-paper/20 to-transparent"
          animate={{ x: ["-200%", "200%"] }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        />
      )}

      {loading ? (
        <>
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>AI 正在推演最佳大学生活...</span>
        </>
      ) : (
        <>
          <Sparkles className="h-5 w-5" />
          <span>生成我的 AI 课表</span>
        </>
      )}
    </motion.button>
  );
}
