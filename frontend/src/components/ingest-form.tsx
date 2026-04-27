"use client"

import { useCallback, useId, useRef, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useIngest } from "@/hooks/use-ingest"
import {
  Upload,
  FileCode,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader2,
  Files,
  X,
  Sparkles,
} from "lucide-react"

interface FileItem {
  file: File
  status: "pending" | "uploading" | "success" | "error"
  message?: string
}

export function IngestForm() {
  const inputId = useId()
  const [files, setFiles] = useState<FileItem[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const [isDragOver, setIsDragOver] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const { ingest } = useIngest({
    onSuccess: (result) => {
      setFiles((prev) =>
        prev.map((f) => {
          if (f.status !== "uploading") return f
          const doc = result.documents.find((d) => d.filename === f.file.name)
          return doc
            ? { ...f, status: "success", message: `${doc.chunkCount} chunks` }
            : { ...f, status: "error", message: "not processed" }
        }),
      )
      setErrors((prev) => [...prev, ...result.errors])
    },
    onError: (error) => {
      setFiles((prev) =>
        prev.map((f) => (f.status === "uploading" ? { ...f, status: "error", message: error } : f)),
      )
      setErrors((prev) => [...prev, error])
    },
  })

  const onSelectFiles = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected = Array.from(e.target.files ?? [])
      if (selected.length === 0) return

      setFiles((prev) => [
        ...prev,
        ...selected.map((f) => ({ file: f, status: "pending" as const })),
      ])
      setErrors([])

      setFiles((prev) =>
        prev.map((f) => (f.status === "pending" ? { ...f, status: "uploading" as const } : f)),
      )
      ingest(selected)
      e.target.value = ""
    },
    [ingest],
  )

  const removeFile = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)
      const dropped = Array.from(e.dataTransfer.files).filter(
        (f) => f.name.endsWith(".md") || f.name.endsWith(".py"),
      )
      if (dropped.length === 0) return

      setFiles((prev) => [
        ...prev,
        ...dropped.map((f) => ({ file: f, status: "pending" as const })),
      ])
      setErrors([])

      setFiles((prev) =>
        prev.map((f) => (f.status === "pending" ? { ...f, status: "uploading" as const } : f)),
      )
      ingest(dropped)
      if (inputRef.current) inputRef.current.value = ""
    },
    [ingest],
  )

  const iconFor = (name: string) =>
    name.endsWith(".py") ? <FileCode className="h-4 w-4" /> : <FileText className="h-4 w-4" />

  const processedCount = files.filter((item) => item.status === "success").length
  const uploadingCount = files.filter((item) => item.status === "uploading").length
  const totalChunks = files.reduce((total, item) => {
    const chunks = item.message?.match(/^(\d+) chunks$/)?.[1]
    return total + (chunks ? Number(chunks) : 0)
  }, 0)

  return (
    <Card className="mx-auto w-full max-w-lg overflow-hidden rounded-lg border-pearl-aqua-700 bg-white shadow-sm transition-shadow hover:shadow-md">
      <CardHeader className="border-b border-pearl-aqua-700/50 bg-gradient-to-r from-alice-blue-900/80 via-white to-almond-silk-900/30">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2.5 text-base">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-stormy-teal to-stormy-teal-400 text-white shadow-sm">
              <Upload className="h-4 w-4" />
            </span>
            Ingest Documents
          </CardTitle>
          {files.length > 0 && (
            <span className="rounded-full bg-stormy-teal/10 px-2.5 py-0.5 text-xs font-medium text-stormy-teal">
              {files.length} file{files.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
        <CardDescription className="text-sm leading-6 text-gray-500">
          Upload{" "}
          <code className="rounded bg-pearl-aqua-900 px-1 py-0.5 text-xs font-mono text-stormy-teal">
            .md
          </code>{" "}
          or{" "}
          <code className="rounded bg-pearl-aqua-900 px-1 py-0.5 text-xs font-mono text-stormy-teal">
            .py
          </code>{" "}
          files (max 500 KB each)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 p-4">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault()
              inputRef.current?.click()
            }
          }}
          role="button"
          tabIndex={0}
          className={`group flex cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed px-4 py-7 text-center transition-all ${
            isDragOver
              ? "border-stormy-teal bg-stormy-teal/5 shadow-inner"
              : "border-pearl-aqua-600 bg-alice-blue-900/50 hover:border-stormy-teal hover:bg-stormy-teal/5"
          }`}
        >
          <span
            className={`flex h-12 w-12 items-center justify-center rounded-xl transition-all ${
              isDragOver
                ? "scale-110 bg-stormy-teal text-white shadow-lg"
                : "bg-gradient-to-br from-pearl-aqua-800 to-pearl-aqua-900 text-stormy-teal shadow-sm group-hover:scale-105 group-hover:bg-stormy-teal group-hover:text-white"
            }`}
          >
            <Files className="h-5 w-5" />
          </span>
          <span className="space-y-1.5">
            <span className="block text-sm font-medium text-gray-700">
              {isDragOver ? "Drop files here" : "Choose or drag files"}
            </span>
            <span className="block text-xs leading-5 text-gray-400">
              Markdown notes, READMEs, ADRs, or Python modules
            </span>
          </span>
          <Input
            id={inputId}
            ref={inputRef}
            type="file"
            multiple
            accept=".md,.py"
            className="sr-only"
            onChange={onSelectFiles}
          />
        </div>

        <div className="grid grid-cols-3 gap-2.5">
          <div className="rounded-lg border border-pearl-aqua-700/50 bg-gradient-to-b from-alice-blue-900 to-white p-3 shadow-sm">
            <p className="text-xs text-gray-400">Files</p>
            <p className="mt-1 text-xl font-semibold text-gray-800">{files.length}</p>
          </div>
          <div className="rounded-lg border border-pearl-aqua-700/50 bg-gradient-to-b from-pearl-aqua-900 to-white p-3 shadow-sm">
            <p className="text-xs text-gray-400">Processed</p>
            <p className="mt-1 text-xl font-semibold text-stormy-teal">{processedCount}</p>
          </div>
          <div className="rounded-lg border border-pearl-aqua-700/50 bg-gradient-to-b from-almond-silk-900 to-white p-3 shadow-sm">
            <p className="text-xs text-gray-400">Chunks</p>
            <div className="flex items-baseline gap-1">
              <span className="mt-1 text-xl font-semibold text-tangerine-dream-400">
                {totalChunks}
              </span>
              {uploadingCount > 0 && <Loader2 className="h-3 w-3 animate-spin text-stormy-teal" />}
            </div>
          </div>
        </div>

        {files.length > 0 && (
          <ul className="space-y-1.5">
            {files.map((item, i) => (
              <li
                key={`${item.file.name}-${i}`}
                className="group flex items-center gap-3 rounded-lg border border-pearl-aqua-700/30 bg-white px-3 py-2.5 text-sm shadow-sm transition-all hover:border-pearl-aqua-600 hover:shadow-md"
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-alice-blue-600 to-alice-blue-900 text-stormy-teal shadow-sm">
                  {iconFor(item.file.name)}
                </span>
                <div className="min-w-0 flex-1">
                  <span className="block truncate font-medium text-gray-800">{item.file.name}</span>
                  <span className="text-xs text-gray-400">
                    {(item.file.size / 1024).toFixed(1)} KB
                    {item.message ? ` · ${item.message}` : ""}
                  </span>
                </div>
                <div className="flex shrink-0 items-center gap-1">
                  {item.status === "uploading" && (
                    <Loader2 className="h-4 w-4 animate-spin text-stormy-teal" />
                  )}
                  {item.status === "success" && (
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-stormy-teal/10">
                      <CheckCircle className="h-4 w-4 text-stormy-teal" />
                    </span>
                  )}
                  {item.status === "error" && (
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-red-50">
                      <AlertCircle className="h-4 w-4 text-red-400" />
                    </span>
                  )}
                  {item.status === "pending" && (
                    <button
                      type="button"
                      onClick={() => removeFile(i)}
                      className="rounded-md p-1.5 text-gray-300 opacity-0 transition-all hover:bg-red-50 hover:text-red-400 group-hover:opacity-100"
                      aria-label={`Remove ${item.file.name}`}
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}

        {errors.length > 0 && (
          <div className="animate-slide-up rounded-lg border border-red-200 bg-red-50/80 p-3 text-sm text-red-600">
            <div className="flex items-start gap-2">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <div className="space-y-1">
                {errors.map((err, i) => (
                  <p key={i}>{err}</p>
                ))}
              </div>
            </div>
          </div>
        )}

        {files.length === 0 && !errors.length && (
          <div className="flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-stormy-teal/5 to-pearl-aqua-900/30 px-3 py-2.5 text-xs text-gray-400">
            <Sparkles className="h-3.5 w-3.5 text-stormy-teal" />
            <span>
              Accepted formats: <code className="font-mono text-stormy-teal">.md</code> and{" "}
              <code className="font-mono text-stormy-teal">.py</code>
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
