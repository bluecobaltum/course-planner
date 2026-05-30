import { useState, useRef, useCallback } from "react";
import { Upload, Camera, ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { importImage } from "@/api/schedule";
import type { ImportResult } from "@/types/schedule";

interface ImportImageProps {
  onResult: (result: ImportResult) => void;
  onError: (msg: string) => void;
  onLoading: (loading: boolean) => void;
}

export default function ImportImage({
  onResult,
  onError,
  onLoading,
}: ImportImageProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    const ext = f.name.split(".").pop()?.toLowerCase();
    if (ext !== "png" && ext !== "jpg" && ext !== "jpeg") {
      onError("请上传 png / jpg / jpeg 格式的图片");
      return;
    }
    setFile(f);
    onError("");

    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result as string);
    reader.readAsDataURL(f);
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

  const handleRecognize = async () => {
    if (!file) return;
    onLoading(true);
    try {
      const result = await importImage(file);
      onResult(result);
    } catch (e) {
      onError(e instanceof Error ? e.message : "图片识别失败");
    } finally {
      onLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          上传课程截图
        </span>
        <Camera className="h-3.5 w-3.5 text-text-tertiary" />
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-8 transition-all cursor-pointer ${
          dragging
            ? "border-accent/50 bg-accent/5"
            : "border-border/60 hover:border-accent/30 hover:bg-surface-secondary/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".png,.jpg,.jpeg"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleFile(f);
          }}
          className="hidden"
        />

        {preview ? (
          <img
            src={preview}
            alt="Preview"
            className="max-h-48 rounded-xl border border-border/40 shadow-sm"
          />
        ) : (
          <>
            <ImageIcon className="h-10 w-10 text-text-tertiary" />
            <span className="text-sm font-medium text-text-primary">
              拖拽截图到此处，或点击选择
            </span>
            <span className="text-xs text-text-tertiary">
              支持 png / jpg / jpeg
            </span>
          </>
        )}
      </div>

      <Button
        variant="accent"
        size="lg"
        className="w-full"
        disabled={!file}
        onClick={handleRecognize}
      >
        <Camera className="h-4 w-4" />
        开始识别
      </Button>
    </div>
  );
}
