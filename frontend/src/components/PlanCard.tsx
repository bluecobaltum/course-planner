import { useState } from "react";
import { motion } from "framer-motion";
import { Lightbulb, Trophy, Clock, GraduationCap, MapPin, ChevronDown } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import CourseRow from "./CourseRow";
import ScoreBar from "./ScoreBar";
import ScheduleGrid from "./ScheduleGrid";
import { getPlanLabel } from "@/utils/label";
import { joinStrategies } from "@/utils/strategy";
import type { Plan } from "@/types/schedule";
import type { Strategy } from "@/types/strategy";

interface PlanCardProps {
  plan: Plan;
  scenario: string;
  strategies: Strategy[];
  index: number;
}

const SCORE_LABELS: Record<string, string> = {
  gpa_score: "GPA 友好",
  compact_score: "紧凑度",
  stress_score: "学业压力",
  free_score: "空闲半日",
  morning_penalty: "早八友好",
  friday_penalty: "周五友好",
  monday_penalty: "周一友好",
  afternoon_penalty: "下午自由",
};

const QUICK_STATS = [
  { key: "total_credits", icon: GraduationCap, label: "学分", unit: "" },
  { key: "school_days", icon: MapPin, label: "上课天数", unit: "天" },
  { key: "earliest_period", icon: Clock, label: "最早节次", unit: "节" },
] as const;

export default function PlanCard({
  plan,
  scenario,
  strategies,
  index,
}: PlanCardProps) {
  const label = getPlanLabel(scenario, plan.rank);
  const matchedStrategies = joinStrategies(
    plan.matched_strategies,
    strategies
  );
  const { analysis } = plan;
  const [showAllCourses, setShowAllCourses] = useState(false);

  const scorePct = plan.score / 10; // 0..1
  const circumference = 2 * Math.PI * 28;
  const offset = circumference * (1 - scorePct);

  const displayCourses = showAllCourses
    ? plan.courses
    : plan.courses.slice(0, 5);
  const hiddenCount = plan.courses.length - 5;

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.15, duration: 0.5 }}
    >
      <Card className="overflow-hidden border-accent/10 hover:border-accent/20 transition-all duration-300">
        {/* ── Header ── */}
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              {/* Rank badge */}
              <div
                className="flex h-10 w-10 items-center justify-center rounded-xl text-lg font-bold"
                style={{
                  background:
                    plan.rank === 1
                      ? "linear-gradient(135deg, #fbbf24, #f59e0b)"
                      : plan.rank === 2
                        ? "linear-gradient(135deg, #94a3b8, #64748b)"
                        : "linear-gradient(135deg, #d6a074, #b87351)",
                  color: "white",
                }}
              >
                {plan.rank === 1 ? (
                  <Trophy className="h-5 w-5" />
                ) : (
                  plan.rank
                )}
              </div>

              <div>
                <CardTitle className="text-xl">{label}</CardTitle>
                <div className="flex items-center gap-3 mt-1">
                  {/* Score Ring */}
                  <svg width="64" height="64" className="flex-shrink-0">
                    <circle
                      cx="32" cy="32" r="28"
                      fill="none"
                      stroke="currentColor"
                      className="text-border/40"
                      strokeWidth="4"
                    />
                    <circle
                      cx="32" cy="32" r="28"
                      fill="none"
                      stroke="url(#scoreGrad)"
                      strokeWidth="4"
                      strokeLinecap="round"
                      strokeDasharray={circumference}
                      strokeDashoffset={offset}
                      transform="rotate(-90 32 32)"
                      className="transition-all duration-1000 ease-out"
                    />
                    <defs>
                      <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#6366f1" />
                        <stop offset="100%" stopColor="#818cf8" />
                      </linearGradient>
                    </defs>
                    <text
                      x="32" y="32"
                      textAnchor="middle"
                      dominantBaseline="central"
                      className="text-xs font-bold"
                      fill="currentColor"
                    >
                      {plan.score.toFixed(1)}
                    </text>
                  </svg>
                  <span className="text-xs text-text-tertiary">综合评分</span>
                </div>
              </div>
            </div>

            {/* Quick stats */}
            <div className="hidden sm:flex items-center gap-4">
              {QUICK_STATS.map(({ key, icon: Icon, label: statLabel, unit }) => {
                const val =
                  key === "total_credits"
                    ? analysis.total_credits
                    : key === "school_days"
                      ? analysis.school_days
                      : analysis.earliest_period;
                return (
                  <div key={key} className="text-center">
                    <div className="flex items-center justify-center gap-1 text-text-tertiary">
                      <Icon className="h-3.5 w-3.5" />
                      <span className="text-[10px]">{statLabel}</span>
                    </div>
                    <div className="text-lg font-semibold text-text-primary">
                      {val}
                      <span className="text-xs font-normal text-text-tertiary ml-0.5">
                        {unit}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-5">
          {/* ── Course List ── */}
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
              课程列表
            </span>
            <div className="mt-2 space-y-1.5">
              {displayCourses.map((course) => (
                <CourseRow key={course.section_id} course={course} />
              ))}
              {hiddenCount > 0 && !showAllCourses && (
                <button
                  onClick={() => setShowAllCourses(true)}
                  className="flex items-center gap-1.5 w-full justify-center py-2 text-xs font-medium text-accent hover:text-accent-dark transition-colors cursor-pointer"
                >
                  <ChevronDown className="h-3.5 w-3.5" />
                  展开全部 {plan.courses.length} 门课程（还有 {hiddenCount} 门）
                </button>
              )}
              {showAllCourses && hiddenCount > 0 && (
                <button
                  onClick={() => setShowAllCourses(false)}
                  className="flex items-center gap-1.5 w-full justify-center py-2 text-xs font-medium text-text-tertiary hover:text-text-secondary transition-colors cursor-pointer"
                >
                  收起课程列表
                </button>
              )}
            </div>
          </div>

          {/* ── Score Breakdown ── */}
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
              维度评分
            </span>
            <div className="mt-2 space-y-1.5">
              {Object.entries(SCORE_LABELS).map(([key, labelText]) => (
                <ScoreBar
                  key={key}
                  label={labelText}
                  value={
                    analysis.score_breakdown[
                      key as keyof typeof analysis.score_breakdown
                    ]
                  }
                />
              ))}
            </div>
          </div>

          {/* ── AI Reasons ── */}
          {analysis.reasons.length > 0 && (
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
                AI 推荐理由
              </span>
              <ul className="mt-2 space-y-1.5">
                {analysis.reasons.map((reason, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-text-secondary"
                  >
                    <Lightbulb className="h-4 w-4 text-amber-400 flex-shrink-0 mt-0.5" />
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* ── Mini Schedule Grid ── */}
          <ScheduleGrid courses={plan.courses} />

          {/* ── Matched Strategies ── */}
          {matchedStrategies.length > 0 && (
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
                AI 选课技巧
              </span>
              <div className="mt-2 flex flex-wrap gap-2">
                {matchedStrategies.map((s) => (
                  <Badge
                    key={s.id}
                    variant="purple"
                    className="gap-1.5 px-2.5 py-1.5 cursor-default"
                  >
                    <span>{s.icon}</span>
                    <span className="text-xs font-medium">{s.title}</span>
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
