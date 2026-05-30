import { motion } from "framer-motion";
import { BookOpen, Download, Database } from "lucide-react";

const NAV_ITEMS = [
  { id: "schedule", label: "选课方案", icon: BookOpen },
  { id: "import", label: "导入课程", icon: Download },
  { id: "courses", label: "课程数据", icon: Database },
] as const;

interface PageNavProps {
  active: string;
  onNavigate: (tab: string) => void;
}

export default function PageNav({ active, onNavigate }: PageNavProps) {
  return (
    <div className="flex items-center justify-center gap-4">
      {NAV_ITEMS.map((item) => {
        const Icon = item.icon;
        const isActive = item.id === active;
        return (
          <motion.button
            key={item.id}
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => onNavigate(item.id)}
            className={`group relative flex items-center gap-3 rounded-2xl border px-7 py-3.5 text-base font-semibold transition-all duration-300 cursor-pointer ${
              isActive
                ? "border-amber-200/70 bg-amber-50/60 text-amber-700 shadow-sm"
                : "border-border/60 bg-paper/60 text-text-secondary hover:border-amber-200/50 hover:bg-amber-50/40 hover:text-amber-600"
            }`}
          >
            <Icon
              className={`h-5 w-5 transition-colors ${
                isActive
                  ? "text-amber-500"
                  : "text-text-tertiary group-hover:text-amber-400"
              }`}
            />
            <span>{item.label}</span>
            {isActive && (
              <motion.span
                layoutId="pageNavDot"
                className="absolute -top-1.5 -right-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-accent text-[9px] font-bold text-white shadow-sm"
                transition={{ type: "spring", stiffness: 600, damping: 30 }}
              >
                ●
              </motion.span>
            )}
          </motion.button>
        );
      })}
    </div>
  );
}
