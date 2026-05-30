import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const LOADING_MESSAGES = [
  "正在分析课程冲突...",
  "正在计算最优课表...",
  "正在评估教师评分...",
  "正在权衡早八和 GPA...",
  "正在为你的大学生活做数学建模...",
  "正在生成最佳选课策略...",
];

interface LoadingOverlayProps {
  visible: boolean;
}

export default function LoadingOverlay({ visible }: LoadingOverlayProps) {
  const [index, setIndex] = useState(0);
  const [dots, setDots] = useState("");

  useEffect(() => {
    if (!visible) return;

    const msgTimer = setInterval(() => {
      setIndex((prev) => (prev + 1) % LOADING_MESSAGES.length);
    }, 1200);

    const dotTimer = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? "" : prev + "."));
    }, 400);

    return () => {
      clearInterval(msgTimer);
      clearInterval(dotTimer);
    };
  }, [visible]);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-golden-hour/85"
        >
          <div className="flex flex-col items-center gap-8 text-center">
            {/* AI pulse ring */}
            <div className="relative">
              <motion.div
                className="absolute inset-0 rounded-full bg-accent/20"
                animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              />
              <motion.div
                className="absolute inset-0 rounded-full bg-accent/10"
                animate={{ scale: [1, 2, 1], opacity: [0.3, 0, 0.3] }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.5,
                }}
              />
              <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-paper shadow-lg border border-accent/20">
                <span className="text-3xl">🧠</span>
              </div>
            </div>

            {/* Rotating message */}
            <div className="min-h-[3rem] flex items-center justify-center">
              <AnimatePresence mode="wait">
                <motion.p
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="text-base font-medium text-text-primary"
                >
                  {LOADING_MESSAGES[index]}
                  <span className="inline-block w-6 text-left text-accent">
                    {dots}
                  </span>
                </motion.p>
              </AnimatePresence>
            </div>

            {/* Progress bar (indeterminate) */}
            <div className="h-1 w-48 overflow-hidden rounded-full bg-border/50">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-accent to-accent-light"
                animate={{ x: ["-100%", "200%"] }}
                transition={{
                  duration: 1.8,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
                style={{ width: "40%" }}
              />
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
