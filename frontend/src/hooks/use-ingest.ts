import { validateFile } from "@/domain/value-objects"
import { ingestFiles, type IngestDocumentsResponse } from "@/infrastructure/api/client"

export interface UseIngestOptions {
  onSuccess?: (result: IngestDocumentsResponse) => void
  onError?: (error: string) => void
}

export function useIngest({ onSuccess, onError }: UseIngestOptions = {}) {
  async function ingest(fileList: FileList | File[]) {
    const files = Array.from(fileList)

    for (const file of files) {
      const validation = validateFile(file.name, file.size)
      if (!validation.valid) {
        onError?.(validation.error)
        return
      }
    }

    try {
      const result = await ingestFiles(files)
      onSuccess?.(result)
    } catch (err) {
      onError?.(err instanceof Error ? err.message : "Error inesperado")
    }
  }

  return { ingest }
}
