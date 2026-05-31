export interface PromptPreset {
  id: string;
  label: string;
  icon: string;
  prompt: string;
  order: number; // 排序权重，越小越靠前。0=最高优先级
}

export const PROMPT_PRESETS: PromptPreset[] = [
  {
    id: "compact_days",
    label: "空闲日最大化",
    icon: "🗓",
    order: 0,
    prompt: `请按以下原则选课：
1. 最大化完全空闲日，把课程压缩到2-3天内
2. 每天有课的日子里课程连续紧凑，减少课间空档
3. 可以接受早八和晚课来换取更多完整空闲日
4. 体育课只选1门
5. 冲突时宁可少选课也不要破坏压缩天数原则`,
  },
  {
    id: "custom",
    label: "自定义",
    icon: "✏️",
    order: 999, // 永远在最后
    prompt: "",
  },
];

/** 按 order 排序后的预设列表（"自定义"始终垫底） */
export const SORTED_PRESETS = [...PROMPT_PRESETS].sort((a, b) => a.order - b.order);
