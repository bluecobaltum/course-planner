const LABELS: Record<string, string[]> = {
  gpa_focus: ["GPA King", "稳健高分流", "生存优先方案"],
  no_morning: ["睡眠守护者", "平衡方案", "极限 GPA 方案"],
  long_weekend: ["周末战神", "三天假期方案", "折中方案"],
  balanced: ["时间管理大师", "紧凑方案", "灵活方案"],
  easy_mode: ["躺平冠军", "低压方案", "轻度勤奋"],
};

export function getPlanLabel(scenario: string, rank: number): string {
  const labels = LABELS[scenario];
  if (labels && rank >= 1 && rank <= labels.length) {
    return labels[rank - 1];
  }
  return `方案 ${"ABC"[Math.min(rank - 1, 2)]}`;
}
