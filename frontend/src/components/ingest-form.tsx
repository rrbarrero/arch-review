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
        (f) =>
          f.name.endsWith(".md") ||
          f.name.endsWith(".py") ||
          f.name.endsWith(".toml") ||
          f.name.endsWith(".json") ||
          f.name.endsWith(".txt") ||
          f.name.endsWith(".ts") ||
          f.name.endsWith(".yml") ||
          f.name.endsWith(".yaml"),
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

  const iconFor = (name: string) => {
    const codeFiles = [".py", ".ts", ".json", ".toml"]
    return codeFiles.some((ext) => name.endsWith(ext)) ? (
      <FileCode className="h-4 w-4" />
    ) : (
      <FileText className="h-4 w-4" />
    )
  }

  const processedCount = files.filter((item) => item.status === "success").length
  const uploadingCount = files.filter((item) => item.status === "uploading").length
  const totalChunks = files.reduce((total, item) => {
    const chunks = item.message?.match(/^(\d+) chunks$/)?.[1]
    return total + (chunks ? Number(chunks) : 0)
  }, 0)

  return (
    <Card className="mx-auto w-full max-w-lg overflow-hidden">
      <CardHeader className="border-b border-border bg-card">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2.5 text-base tracking-normal text-console-ink">
            <span className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground shadow-sm">
              <Upload className="h-4 w-4" />
            </span>
            Ingest Documents
          </CardTitle>
          {files.length > 0 && (
            <span className="min-w-16 rounded-full border border-border bg-console-panel-muted px-2.5 py-0.5 text-center text-xs font-medium text-console-secondary">
              {files.length} file{files.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
        <CardDescription className="text-sm leading-6 text-console-muted">
          Upload{" "}
          <code className="rounded bg-console-code px-1 py-0.5 font-mono text-xs text-console-primary">
            .md
          </code>
          ,{" "}
          <code className="rounded bg-console-code px-1 py-0.5 font-mono text-xs text-console-primary">
            .py
          </code>
          ,{" "}
          <code className="rounded bg-console-code px-1 py-0.5 font-mono text-xs text-console-primary">
            .toml
          </code>
          ,{" "}
          <code className="rounded bg-console-code px-1 py-0.5 font-mono text-xs text-console-primary">
            .json
          </code>
          ,{" "}
          <code className="rounded bg-console-code px-1 py-0.5 font-mono text-xs text-console-primary">
            .txt
          </code>
          ,{" "}
          <code className="rounded bg-console-code px-1 py-0.5 font-mono text-xs text-console-primary">
            .ts
          </code>
          ,{" "}
          <code className="rounded bg-console-code px-1 py-0.5 font-mono text-xs text-console-primary">
            .yml
          </code>{" "}
          or{" "}
          <code className="rounded bg-console-code px-1 py-0.5 font-mono text-xs text-console-primary">
            .yaml
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
          className={`group flex cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border border-dashed px-4 py-7 text-center transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/25 ${
            isDragOver
              ? "border-primary bg-primary/5 shadow-inner"
              : "border-border bg-console-panel-muted hover:border-primary/60 hover:bg-primary/5"
          }`}
        >
          <span
            className={`flex h-12 w-12 items-center justify-center rounded-lg transition-colors ${
              isDragOver
                ? "bg-primary text-primary-foreground shadow-sm"
                : "bg-card text-console-primary shadow-sm group-hover:bg-primary group-hover:text-primary-foreground"
            }`}
          >
            <Files className="h-5 w-5" />
          </span>
          <span className="space-y-1.5">
            <span className="block text-sm font-medium text-console-ink">
              {isDragOver ? "Drop files here" : "Choose or drag files"}
            </span>
            <span className="block text-xs leading-5 text-console-muted">
              Markdown, Python, TOML, JSON, text, TypeScript, or YAML files
            </span>
          </span>
          <Input
            id={inputId}
            ref={inputRef}
            type="file"
            multiple
            accept=".md,.py,.toml,.json,.txt,.ts,.yml,.yaml"
            className="sr-only"
            aria-label="Choose or drag files"
            onChange={onSelectFiles}
          />
        </div>

        <div className="grid grid-cols-3 gap-2.5">
          <div className="rounded-lg border border-border bg-card p-3 shadow-sm">
            <p className="text-xs text-console-muted">Files</p>
            <p className="mt-1 text-xl font-semibold text-console-ink">{files.length}</p>
          </div>
          <div className="rounded-lg border border-border bg-card p-3 shadow-sm">
            <p className="text-xs text-console-muted">Processed</p>
            <p className="mt-1 text-xl font-semibold text-console-success">{processedCount}</p>
          </div>
          <div className="rounded-lg border border-border bg-card p-3 shadow-sm">
            <p className="text-xs text-console-muted">Chunks</p>
            <div className="flex items-baseline gap-1">
              <span className="mt-1 text-xl font-semibold text-console-accent">{totalChunks}</span>
              {uploadingCount > 0 && <Loader2 className="h-3 w-3 animate-spin text-primary" />}
            </div>
          </div>
        </div>

        {files.length > 0 && (
          <ul className="space-y-1.5">
            {files.map((item, i) => (
              <li
                key={`${item.file.name}-${i}`}
                className="group flex items-center gap-3 rounded-lg border border-border bg-card px-3 py-2.5 text-sm shadow-sm transition-colors hover:border-primary/40 hover:bg-console-panel-muted/60"
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-console-panel-muted text-console-primary shadow-sm">
                  {iconFor(item.file.name)}
                </span>
                <div className="min-w-0 flex-1">
                  <span className="block truncate font-medium text-console-ink">
                    {item.file.name}
                  </span>
                  <span className="font-mono text-xs text-console-muted">
                    {(item.file.size / 1024).toFixed(1)} KB
                    {item.message ? ` · ${item.message}` : ""}
                  </span>
                </div>
                <div className="flex shrink-0 items-center gap-1">
                  {item.status === "uploading" && (
                    <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  )}
                  {item.status === "success" && (
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-console-success/10">
                      <CheckCircle className="h-4 w-4 text-console-success" />
                    </span>
                  )}
                  {item.status === "error" && (
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-console-danger/10">
                      <AlertCircle className="h-4 w-4 text-console-danger" />
                    </span>
                  )}
                  {item.status === "pending" && (
                    <button
                      type="button"
                      onClick={() => removeFile(i)}
                      className="rounded-md p-1.5 text-console-muted opacity-0 transition-colors hover:bg-console-danger/10 hover:text-console-danger group-hover:opacity-100"
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
          <div className="animate-slide-up rounded-lg border border-console-danger/30 bg-console-danger/10 p-3 text-sm text-console-danger">
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
          <div className="flex items-center justify-center gap-2 rounded-lg border border-border bg-console-panel-muted px-3 py-2.5 text-xs text-console-muted">
            <Sparkles className="h-3.5 w-3.5 text-console-primary" />
            <span>
              Accepted formats: <code className="font-mono text-console-primary">.md</code>,{" "}
              <code className="font-mono text-console-primary">.py</code>,{" "}
              <code className="font-mono text-console-primary">.toml</code>,{" "}
              <code className="font-mono text-console-primary">.json</code>,{" "}
              <code className="font-mono text-console-primary">.txt</code>,{" "}
              <code className="font-mono text-console-primary">.ts</code>,{" "}
              <code className="font-mono text-console-primary">.yml</code> and{" "}
              <code className="font-mono text-console-primary">.yaml</code>
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
