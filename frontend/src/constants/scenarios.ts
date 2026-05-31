import { Scale, Sun, Compass, Umbrella, Moon } from "lucide-react";
import type { ComponentType } from "react";

export interface ScenarioMeta {
  id: string;
  icon: ComponentType<{ className?: string }>;
  title: string;
  description: string;
  tags: string[];
  weightPreview: string;
}

export const SCENARIOS: ScenarioMeta[] = [
  {
    id: "balanced",
    icon: Scale,
    title: "平衡模式",
    description: "空闲时间、紧凑度、无早八均衡优化，适合大多数人的默认选择",
    tags: ["均衡", "推荐", "全能"],
    weightPreview: "空闲日 × 25% · 紧凑度 × 25% · 无早八 × 20%",
  },
  {
    id: "no_morning",
    icon: Sun,
    title: "无早八模式",
    description: "最大化减少1-2节早课，让你每天自然醒",
    tags: ["无早八", "自然醒", "睡眠优先"],
    weightPreview: "无早八 × 60% · 紧凑度 × 15% · 空闲日 × 10%",
  },
  {
    id: "compact",
    icon: Compass,
    title: "紧凑模式",
    description: "课程连续集中，减少课间空档，最大化连续自由时间块",
    tags: ["集中排课", "大块空闲", "高效节奏"],
    weightPreview: "紧凑度 × 65% · 无早八 × 15% · 无晚课 × 10%",
  },
  {
    id: "leisurely",
    icon: Umbrella,
    title: "休闲模式",
    description: "尽量压缩上课天数，最大化完整空闲日，适合实习/社团",
    tags: ["空闲优先", "压缩天数", "自由时间"],
    weightPreview: "空闲日 × 60% · 无早八 × 15% · 紧凑度 × 10%",
  },
  {
    id: "no_night",
    icon: Moon,
    title: "无晚课模式",
    description: "减少11-14节晚课，晚上时间完全属于自己",
    tags: ["无晚课", "晚间自由", "早睡友好"],
    weightPreview: "无晚课 × 60% · 紧凑度 × 15% · 空闲日 × 10%",
  },
];

export const SCENARIO_MAP = Object.fromEntries(
  SCENARIOS.map((s) => [s.id, s])
) as Record<string, ScenarioMeta>;

export const EASY_MAX = 5;
