import { useState } from "react";
import ThemeToggle from "@/components/common/ThemeToggle";
import Home from "@/pages/Home";
import CourseManager from "@/components/CourseManager";
import ImportCenter from "@/components/import/ImportCenter";
import PageNav from "@/components/PageNav";

export default function App() {
  const [activeTab, setActiveTab] = useState<string>("schedule");

  return (
    <div className="min-h-screen bg-grid">
      <div className="sticky top-0 z-40 border-b border-border/40 bg-paper/70 backdrop-blur-xl">
        <div className="mx-auto max-w-6xl px-4 flex items-center justify-center py-3 relative">
          <PageNav active={activeTab} onNavigate={setActiveTab} />
          <div className="absolute right-4">
            <ThemeToggle />
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-4 py-6">
        <div className={activeTab === "schedule" ? "" : "hidden"}>
          <Home />
        </div>
        <div className={activeTab === "import" ? "" : "hidden"}>
          <ImportCenter />
        </div>
        <div className={activeTab === "courses" ? "" : "hidden"}>
          <CourseManager />
        </div>
      </div>
    </div>
  );
}
