import { motion } from "framer-motion";
import { FileSpreadsheet, Bot, Camera } from "lucide-react";
import { cn } from "@/lib/utils";

interface Method {
  id: "excel" | "text" | "image";
  icon: typeof FileSpreadsheet;
  title: string;
  description: string;
  badges: string[];
  accuracy: string;
  speed: string;
  cost: string;
}

const METHODS: Method[] = [
  {
    id: "excel",
    icon: FileSpreadsheet,
    title: "Excel 导入",
    description: "上传教务系统导出的课程表",
    badges: ["推荐", "准确率最高", "无AI费用"],
    accuracy: "★★★★★",
    speed: "最快",
    cost: "免费",
  },
  {
    id: "text",
    icon: Bot,
    title: "AI 文本解析",
    description: "粘贴课程描述，由 AI 自动结构化",
    badges: ["AI", "灵活输入"],
    accuracy: "★★★★☆",
    speed: "中等",
    cost: "低",
  },
  {
    id: "image",
    icon: Camera,
    title: "图片识别",
    description: "上传课表截图体验智能识别",
    badges: ["Demo", "Vision"],
    accuracy: "★★★☆☆",
    speed: "中等",
    cost: "Demo",
  },
];

interface ImportMethodSelectorProps {
  selected: "excel" | "text" | "image" | null;
  onSelect: (method: "excel" | "text" | "image") => void;
}

export default function ImportMethodSelector({
  selected,
  onSelect,
}: ImportMethodSelectorProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          选择导入方式
        </span>
        <div className="h-px flex-1 bg-border/50" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {METHODS.map((method) => {
          const Icon = method.icon;
          const isSelected = selected === method.id;

          return (
            <motion.button
              key={method.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onSelect(method.id)}
              className={cn(
                "relative flex flex-col items-start gap-3 rounded-2xl border p-5 text-left transition-all duration-300 cursor-pointer",
                isSelected
                  ? "border-accent/60 bg-paper/90 glow ring-1 ring-accent/20"
                  : "border-border/60 bg-paper/60 hover:border-accent/30 hover:bg-paper/80 hover:shadow-md"
              )}
            >
              {isSelected && (
                <motion.div
                  layoutId="importActiveBar"
                  className="absolute top-0 left-4 right-4 h-0.5 rounded-full bg-gradient-to-r from-accent via-accent-light to-accent"
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}

              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-xl transition-colors",
                  isSelected
                    ? "bg-accent/10 text-accent"
                    : "bg-surface-secondary text-text-secondary"
                )}
              >
                <Icon className="h-5 w-5" />
              </div>

              <div className="flex flex-col gap-1">
                <span
                  className={cn(
                    "text-sm font-semibold",
                    isSelected ? "text-accent" : "text-text-primary"
                  )}
                >
                  {method.title}
                </span>
                <span className="text-xs text-text-secondary leading-relaxed">
                  {method.description}
                </span>
              </div>

              <div className="flex flex-wrap gap-1.5">
                {method.badges.map((b) => (
                  <span
                    key={b}
                    className={cn(
                      "inline-block rounded-full px-2 py-0.5 text-[10px] font-medium",
                      isSelected
                        ? "bg-accent/10 text-accent"
                        : "bg-surface-secondary text-text-tertiary"
                    )}
                  >
                    {b}
                  </span>
                ))}
              </div>

              <div className="w-full space-y-0.5 text-[10px] text-text-tertiary mt-auto">
                <div className="flex justify-between">
                  <span>准确率</span>
                  <span className="text-amber-500">{method.accuracy}</span>
                </div>
                <div className="flex justify-between">
                  <span>速度</span>
                  <span>{method.speed}</span>
                </div>
                <div className="flex justify-between">
                  <span>费用</span>
                  <span>{method.cost}</span>
                </div>
              </div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
