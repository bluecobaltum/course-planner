const LABELS: Record<string, string[]> = {
  balanced:   ["均衡方案", "日常优选", "弹性方案"],
  no_morning: ["睡眠守护者", "自然醒方案", "早课最少"],
  compact:    ["时间管理大师", "紧凑方案", "高效方案"],
  leisurely:  ["自由之翼", "休闲冠军", "压缩方案"],
  no_night:   ["晚间自由", "早睡方案", "夜课最少"],
};

export function getPlanLabel(scenario: string, rank: number): string {
  const labels = LABELS[scenario];
  if (labels && rank >= 1 && rank <= labels.length) {
    return labels[rank - 1];
  }
  return `方案 ${"ABC"[Math.min(rank - 1, 2)]}`;
}
