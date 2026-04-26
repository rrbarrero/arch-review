"use client"

import { useCallback, useRef, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useIngest } from "@/hooks/use-ingest"
import { Upload, FileCode, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react"

interface FileItem {
  file: File
  status: "pending" | "uploading" | "success" | "error"
  message?: string
}

export function IngestForm() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const inputRef = useRef<HTMLInputElement>(null)
  const { ingest } = useIngest({
    onSuccess: (result) => {
      setFiles((prev) =>
        prev.map((f) => {
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
    },
    [ingest],
  )

  const removeFile = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }, [])

  const iconFor = (name: string) =>
    name.endsWith(".py") ? <FileCode className="h-4 w-4" /> : <FileText className="h-4 w-4" />

  return (
    <Card className="w-full max-w-lg mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Ingest Documents
        </CardTitle>
        <CardDescription>
          Upload <code>.md</code> or <code>.py</code> files (max 500 KB each)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-2">
          <Input
            ref={inputRef}
            type="file"
            multiple
            accept=".md,.py"
            className="cursor-pointer"
            onChange={onSelectFiles}
          />
        </div>

        {files.length > 0 && (
          <ul className="space-y-2">
            {files.map((item, i) => (
              <li key={`${item.file.name}-${i}`} className="flex items-center gap-2 text-sm">
                {iconFor(item.file.name)}
                <span className="flex-1 truncate">{item.file.name}</span>
                <span className="text-xs text-muted-foreground">
                  {(item.file.size / 1024).toFixed(1)} KB
                </span>
                {item.status === "uploading" && (
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                )}
                {item.status === "success" && <CheckCircle className="h-4 w-4 text-green-500" />}
                {item.status === "error" && <AlertCircle className="h-4 w-4 text-red-500" />}
                {item.status === "pending" && (
                  <button
                    onClick={() => removeFile(i)}
                    className="text-xs text-muted-foreground hover:text-foreground"
                  >
                    ✕
                  </button>
                )}
                {item.message && (
                  <span className="text-xs text-muted-foreground">{item.message}</span>
                )}
              </li>
            ))}
          </ul>
        )}

        {errors.length > 0 && (
          <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive space-y-1">
            {errors.map((err, i) => (
              <p key={i}>{err}</p>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
