import { useState } from "react";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { importText } from "@/api/schedule";
import type { ImportResult } from "@/types/schedule";

const PLACEHOLDER = `课程名称：高等数学
教师：张三
时间：周一1-2节 周三3-4节

课程名称：大学英语
教师：李四
时间：周二3-4节 周四5-6节

课程名称：程序设计
教师：王五
时间：周三6-8节`;

interface ImportTextProps {
  onResult: (result: ImportResult) => void;
  onError: (msg: string) => void;
  onLoading: (loading: boolean) => void;
}

export default function ImportText({
  onResult,
  onError,
  onLoading,
}: ImportTextProps) {
  const [text, setText] = useState("");

  const handleParse = async () => {
    if (!text.trim()) {
      onError("请输入课程描述文本");
      return;
    }
    onLoading(true);
    try {
      const result = await importText(text.trim());
      onResult(result);
    } catch (e) {
      onError(e instanceof Error ? e.message : "AI 解析失败");
    } finally {
      onLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          粘贴课程文本
        </span>
        <Sparkles className="h-3.5 w-3.5 text-accent" />
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={PLACEHOLDER}
        rows={12}
        className="w-full rounded-2xl border border-border/60 bg-paper/70 px-4 py-3 text-sm resize-y focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 placeholder:text-text-tertiary"
      />

      <Button
        variant="accent"
        size="lg"
        className="w-full"
        disabled={!text.trim()}
        onClick={handleParse}
      >
        <Sparkles className="h-4 w-4" />
        开始智能解析
      </Button>
    </div>
  );
}
