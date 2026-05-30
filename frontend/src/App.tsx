import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Database } from "lucide-react";
import Home from "@/pages/Home";
import CourseManager from "@/components/CourseManager";

const TABS = [
  { id: "schedule", label: "选课方案", icon: Sparkles },
  { id: "courses", label: "课程数据", icon: Database },
] as const;

export default function App() {
  const [activeTab, setActiveTab] = useState<string>("schedule");

  return (
    <div className="min-h-screen bg-grid">
      {/* Tab Bar */}
      <div className="sticky top-0 z-40 border-b border-border/40 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto max-w-6xl px-4 flex items-center gap-1 py-2">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-all cursor-pointer ${
                  isActive
                    ? "text-accent"
                    : "text-text-tertiary hover:text-text-secondary"
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
                {isActive && (
                  <motion.div
                    layoutId="tab-active"
                    className="absolute inset-0 rounded-xl bg-accent/8 border border-accent/15"
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="mx-auto max-w-6xl px-4 py-6">
        {activeTab === "schedule" ? <Home /> : <CourseManager />}
      </div>
    </div>
  );
}
