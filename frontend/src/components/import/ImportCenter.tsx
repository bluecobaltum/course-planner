import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/Button";
import LoadingOverlay from "@/components/LoadingOverlay";
import ImportMethodSelector from "@/components/import/ImportMethodSelector";
import ImportExcel from "@/components/import/ImportExcel";
import ImportText from "@/components/import/ImportText";
import ImportImage from "@/components/import/ImportImage";
import ImportResultPreview from "@/components/import/ImportResultPreview";
import type { ImportResult } from "@/types/schedule";

type ImportStep = "select" | "input" | "preview";
type ImportMethod = "excel" | "text" | "image";

export default function ImportCenter() {
  const [step, setStep] = useState<ImportStep>("select");
  const [method, setMethod] = useState<ImportMethod | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string>("");

  const handleSelect = useCallback((m: ImportMethod) => {
    setMethod(m);
    setError("");
    setStep("input");
  }, []);

  const handleResult = useCallback((r: ImportResult) => {
    setResult(r);
    setError("");
    setStep("preview");
  }, []);

  const handleRetry = useCallback(() => {
    setResult(null);
    setError("");
    setStep("input");
  }, []);

  const handleDone = useCallback(() => {
    // Reset back to selection
    setStep("select");
    setMethod(null);
    setResult(null);
    setError("");
  }, []);

  const handleBack = useCallback(() => {
    if (step === "input") {
      setStep("select");
      setMethod(null);
    } else if (step === "preview") {
      setStep("input");
      setResult(null);
    }
    setError("");
  }, [step]);

  return (
    <div className="space-y-5">
      <LoadingOverlay visible={loading} />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {step !== "select" && (
            <Button variant="ghost" size="sm" onClick={handleBack}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
          )}
          <div>
            <h2 className="text-lg font-semibold text-text-primary">
              📥 导入课程
            </h2>
            <p className="text-xs text-text-secondary mt-0.5">
              {step === "select" && "选择一种课程导入方式"}
              {step === "input" && method === "excel" && "上传教务系统导出的 Excel 课表"}
              {step === "input" && method === "text" && "粘贴课程描述文本，AI 自动解析"}
              {step === "input" && method === "image" && "上传课表截图进行识别"}
              {step === "preview" && "预览解析结果，确认后导入课程库"}
            </p>
          </div>
        </div>
      </div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="rounded-xl border border-red-200 bg-red-50/60 px-4 py-3 text-sm text-red-600"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Content */}
      <AnimatePresence mode="wait">
        {step === "select" && (
          <motion.div
            key="select"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <ImportMethodSelector
              selected={method}
              onSelect={handleSelect}
            />
          </motion.div>
        )}

        {step === "input" && method === "excel" && (
          <motion.div
            key="excel"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <ImportExcel
              onResult={handleResult}
              onError={setError}
              onLoading={setLoading}
            />
          </motion.div>
        )}

        {step === "input" && method === "text" && (
          <motion.div
            key="text"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <ImportText
              onResult={handleResult}
              onError={setError}
              onLoading={setLoading}
            />
          </motion.div>
        )}

        {step === "input" && method === "image" && (
          <motion.div
            key="image"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <ImportImage
              onResult={handleResult}
              onError={setError}
              onLoading={setLoading}
            />
          </motion.div>
        )}

        {step === "preview" && result && (
          <motion.div
            key="preview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
          >
            <ImportResultPreview
              result={result}
              onRetry={handleRetry}
              onDone={handleDone}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
