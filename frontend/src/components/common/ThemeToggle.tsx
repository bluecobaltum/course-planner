import { motion } from "framer-motion";
import { Sun, Moon, Monitor } from "lucide-react";
import { useTheme } from "@/lib/ThemeContext";

export default function ThemeToggle() {
  const { theme, cycle } = useTheme();

  return (
    <motion.button
      whileHover={{ scale: 1.08 }}
      whileTap={{ scale: 0.92 }}
      onClick={cycle}
      className="flex h-9 w-9 items-center justify-center rounded-xl border border-border/60 bg-paper/60 backdrop-blur-sm transition-colors hover:border-accent/30 hover:bg-accent/5 cursor-pointer"
      aria-label="切换主题"
      title={
        theme === "light"
          ? "亮色模式"
          : theme === "dark"
            ? "暗色模式"
            : "跟随系统"
      }
    >
      <motion.div
        key={theme}
        initial={{ rotate: -90, opacity: 0, scale: 0.5 }}
        animate={{ rotate: 0, opacity: 1, scale: 1 }}
        transition={{ duration: 0.25, ease: "easeOut" }}
      >
        {theme === "light" && <Sun className="h-4 w-4 text-amber-500" />}
        {theme === "dark" && <Moon className="h-4 w-4 text-amber-300" />}
        {theme === "system" && <Monitor className="h-4 w-4 text-stone" />}
      </motion.div>
    </motion.button>
  );
}
