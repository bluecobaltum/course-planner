import { BookOpen, Sun, Clock, Coffee, Calendar } from "lucide-react";
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
    id: "gpa_focus",
    icon: BookOpen,
    title: "GPA 优先",
    description: "不惜一切代价追求高绩点，即使面临早八和长课日也值得",
    tags: ["高分教师", "学术导向", "品质优先"],
    weightPreview: "GPA × 70% · 紧凑度 × 10% · 压力 × 5%",
  },
  {
    id: "no_morning",
    icon: Sun,
    title: "拒绝早八",
    description: "绝不选第一节早课，上午课程也要尽量减少",
    tags: ["无早八", "自然醒", "睡眠优先"],
    weightPreview: "早八友好 × 15% · 周五友好 × 15% · GPA × 15%",
  },
  {
    id: "long_weekend",
    icon: Calendar,
    title: "快乐长周末",
    description: "周五没课或最少课，享受三天周末的自由时光",
    tags: ["周五自由", "三天周末", "旅行友好"],
    weightPreview: "周五友好 × 30% · 周一友好 × 30% · 紧凑度 × 15%",
  },
  {
    id: "balanced",
    icon: Clock,
    title: "紧凑课表",
    description: "课程集中紧凑，最大化完整自由时间块",
    tags: ["集中排课", "大块空闲", "高效节奏"],
    weightPreview: "紧凑度 × 25% · 空闲半日 × 25% · GPA × 20%",
  },
  {
    id: "easy_mode",
    icon: Coffee,
    title: "摆烂模式",
    description: "学分越少越好，压力越低越好，轻松度过每一学期",
    tags: ["低学分", "低压", "轻松毕业"],
    weightPreview: "压力 × 45% · 空闲半日 × 20% · GPA × 10%",
  },
];

export const SCENARIO_MAP = Object.fromEntries(
  SCENARIOS.map((s) => [s.id, s])
) as Record<string, ScenarioMeta>;

export const EASY_MAX = 5;
