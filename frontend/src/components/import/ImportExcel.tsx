import { useState, useRef, useCallback } from "react";
import { Upload, FileSpreadsheet } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { importExcel } from "@/api/schedule";
import type { ImportResult } from "@/types/schedule";

interface ImportExcelProps {
  onResult: (result: ImportResult) => void;
  onError: (msg: string) => void;
  onLoading: (loading: boolean) => void;
}

export default function ImportExcel({
  onResult,
  onError,
  onLoading,
}: ImportExcelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    const ext = f.name.split(".").pop()?.toLowerCase();
    if (ext !== "xlsx" && ext !== "xls") {
      onError("请上传 .xlsx 或 .xls 格式的 Excel 文件");
      return;
    }
    setFile(f);
    onError("");
  }, [onError]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const f = e.dataTransfer.files[0];
      if (f) handleFile(f);
    },
    [handleFile]
  );

  const handleParse = async () => {
    if (!file) return;
    onLoading(true);
    try {
      const result = await importExcel(file);
      onResult(result);
    } catch (e) {
      onError(e instanceof Error ? e.message : "Excel 解析失败");
    } finally {
      onLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          上传 Excel 文件
        </span>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-10 transition-all cursor-pointer ${
          dragging
            ? "border-accent/50 bg-accent/5"
            : "border-border/60 hover:border-accent/30 hover:bg-surface-secondary/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".xlsx,.xls"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleFile(f);
          }}
          className="hidden"
        />

        {file ? (
          <>
            <FileSpreadsheet className="h-10 w-10 text-emerald-500" />
            <span className="text-sm font-medium text-text-primary">
              {file.name}
            </span>
            <span className="text-xs text-text-tertiary">
              {(file.size / 1024).toFixed(1)} KB · 点击重新选择
            </span>
          </>
        ) : (
          <>
            <Upload className="h-10 w-10 text-text-tertiary" />
            <span className="text-sm font-medium text-text-primary">
              拖拽文件到此处，或点击选择
            </span>
            <span className="text-xs text-text-tertiary">
              支持 .xlsx / .xls 格式
            </span>
          </>
        )}
      </div>

      <Button
        variant="accent"
        size="lg"
        className="w-full"
        disabled={!file}
        onClick={handleParse}
      >
        开始解析
      </Button>
    </div>
  );
}
