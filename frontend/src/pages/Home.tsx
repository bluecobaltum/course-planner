import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, AlertCircle, RefreshCw } from "lucide-react";
import ScenarioSelector from "@/components/ScenarioSelector";
import EasySlider from "@/components/EasySlider";
import GenerateButton from "@/components/GenerateButton";
import LoadingOverlay from "@/components/LoadingOverlay";
import PlanCard from "@/components/PlanCard";
import StrategySection from "@/components/StrategySection";
import { generateSchedule, getStrategies } from "@/api/schedule";
import { filterStrategies } from "@/utils/strategy";
import { PROMPT_PRESETS, SORTED_PRESETS } from "@/constants/prompts";
import type { Plan } from "@/types/schedule";
import type { Strategy } from "@/types/strategy";

export default function Home() {
  const [scenario, setScenario] = useState("balanced");
  const [easyCount, setEasyCount] = useState(1);
  const [loading, setLoading] = useState(false);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [generated, setGenerated] = useState(false);
  const [llmEvaluate, setLlmEvaluate] = useState(false);
  const [llmModel, setLlmModel] = useState("Qwen3.5-27B");
  const [activePreset, setActivePreset] = useState<string>("");
  const [customPrompt, setCustomPrompt] = useState("");

  const MODEL_OPTIONS = [
    { label: "Qwen3.5-27B (快速)", value: "Qwen3.5-27B" },
    { label: "DeepSeek-V4-Flash (推荐)", value: "DeepSeek-V4-Flash" },
    { label: "DeepSeek-V4-Pro (最强)", value: "DeepSeek-V4-Pro" },
    { label: "Qwen3.5-Plus", value: "Qwen3.5-Plus" },
    { label: "GLM-4.7", value: "GLM-4.7" },
  ];

  // Load strategies on mount
  useEffect(() => {
    getStrategies()
      .then((res) => setStrategies(res.strategies))
      .catch(() => setError("无法加载选课策略，请确认后端已启动"));
  }, []);

  const handleGenerate = useCallback(async () => {
    setLoading(true);
    setError(null);
    setGenerated(false);

    try {
      const effectivePrompt = customPrompt.trim() || (activePreset ? PROMPT_PRESETS.find(p => p.id === activePreset)?.prompt || null : null);
      const res = await generateSchedule(scenario, easyCount, llmEvaluate, llmModel, effectivePrompt);
      setPlans(res.plans);
      setGenerated(true);
    } catch (e) {
      const msg =
        e instanceof Error ? e.message : "生成失败，请稍后重试";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [scenario, easyCount, llmEvaluate, llmModel, activePreset, customPrompt]);

  return (
    <div className="min-h-screen bg-grid">
      <LoadingOverlay visible={loading} />

      <div className="mx-auto max-w-6xl px-4 py-8 sm:py-12 lg:py-16 space-y-10">
        {/* ── Hero ── */}
        <motion.div
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-4"
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/5 px-4 py-1.5 text-xs font-medium text-accent">
            <Sparkles className="h-3.5 w-3.5" />
            AI 驱动 · 多维度优化
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-text-primary">
            AI 智能选课助手
          </h1>
          <p className="text-base sm:text-lg text-text-secondary max-w-xl mx-auto leading-relaxed">
            不是帮你排课，而是帮你选择大学生活方式
          </p>
        </motion.div>

        {/* ── Inputs ── */}
        <div className="space-y-8">
          <ScenarioSelector selected={scenario} onSelect={setScenario} />
          <EasySlider value={easyCount} onChange={setEasyCount} />

          {/* ── AI 排课策略 ── */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
                AI 排课策略（可选）
              </span>
              <div className="h-px flex-1 bg-border/50" />
            </div>
            <div className="flex gap-2 flex-wrap">
              {SORTED_PRESETS.map((preset) => (
                <button
                  key={preset.id}
                  onClick={() => {
                    setActivePreset(activePreset === preset.id ? "" : preset.id);
                    if (preset.id !== "custom") setCustomPrompt("");
                  }}
                  className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-medium transition-all cursor-pointer ${
                    activePreset === preset.id
                      ? "border-accent/60 bg-accent/10 text-accent shadow-sm"
                      : "border-border/60 bg-paper/60 text-text-secondary hover:border-accent/30"
                  }`}
                >
                  <span>{preset.icon}</span>
                  <span>{preset.label}</span>
                </button>
              ))}
            </div>
            {activePreset === "custom" && (
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="输入自定义选课偏好，例如：
- 最大化空闲日，课程集中压缩到2-3天
- 不接受早八，晚上不要超过10点
- 物理课优先级最高"
                rows={3}
                className="w-full rounded-xl border border-border/60 bg-paper/70 px-3 py-2 text-xs resize-y focus:outline-none focus:border-accent/50 placeholder:text-text-tertiary"
              />
            )}
          </div>

          <div className="flex flex-col items-center gap-4">
            <div className="flex items-center gap-4 flex-wrap justify-center">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={llmEvaluate}
                  onChange={(e) => setLlmEvaluate(e.target.checked)}
                  className="h-4 w-4 rounded border-border/60 accent-accent cursor-pointer"
                />
                <span className="text-sm text-text-secondary">
                  🤖 AI 智能评估/排课
                </span>
              </label>
              <select
                value={llmModel}
                onChange={(e) => setLlmModel(e.target.value)}
                className="rounded-lg border border-border/60 px-3 py-1.5 text-xs bg-paper focus:outline-none focus:border-accent/50"
              >
                {MODEL_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <GenerateButton
              loading={loading}
              disabled={!scenario}
              onClick={handleGenerate}
            />
          </div>
        </div>

        {/* ── Error ── */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-3 rounded-2xl border border-red-200 bg-red-50/80 backdrop-blur p-4"
            >
              <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
              <span className="text-sm text-red-700 flex-1">{error}</span>
              <button
                onClick={handleGenerate}
                className="flex items-center gap-1.5 text-xs font-medium text-red-600 hover:text-red-800 transition-colors cursor-pointer"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                重试
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Empty State ── */}
        <AnimatePresence>
          {generated && plans.length === 0 && !error && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12 space-y-3"
            >
              <div className="text-5xl">🔍</div>
              <p className="text-lg font-medium text-text-primary">
                当前条件下没有找到理想课表
              </p>
              <p className="text-sm text-text-secondary">
                试试减少水课数量，或切换到不同的选课偏好
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Plan Cards ── */}
        <AnimatePresence>
          {generated && plans.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
                  AI 为你找到 {plans.length} 个方案
                </span>
                <div className="h-px flex-1 bg-border/50" />
              </div>

              <div className="space-y-4">
                {plans.map((plan, i) => (
                  <PlanCard
                    key={plan.id}
                    plan={plan}
                    scenario={scenario}
                    strategies={strategies}
                    index={i}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Strategy Section ── */}
        <StrategySection
          strategies={filterStrategies(strategies, scenario)}
        />
      </div>
    </div>
  );
}
