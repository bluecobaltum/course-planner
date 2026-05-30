const DAY_NAMES = ["", "周一", "周二", "周三", "周四", "周五"];

function dayName(day: number): string {
  return DAY_NAMES[day] || `周${day}`;
}

export function formatPeriods(
  slots: { day: number; start: number; end: number }[]
): string {
  if (slots.length === 0) return "无固定时间（异步网课）";
  return slots
    .map((s) => `${dayName(s.day)} ${s.start}-${s.end}节`)
    .join(" · ");
}

export function ratingStars(rating: number): string {
  const full = Math.round(rating);
  return "★".repeat(full) + "☆".repeat(5 - full);
}

export function deliveryVariant(mode: string): "green" | "purple" | "blue" {
  if (mode === "线上网课") return "green";
  if (mode === "线上线下混合") return "purple";
  return "blue";
}
