const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export interface IngestDocumentResult {
  documentId: string
  filename: string
  chunkCount: number
}

export interface IngestDocumentsResponse {
  documents: IngestDocumentResult[]
  errors: string[]
}

export async function ingestFiles(files: File[]): Promise<IngestDocumentsResponse> {
  const formData = new FormData()
  for (const file of files) {
    formData.append("files", file)
  }

  const res = await fetch(`${API_BASE}/intake/ingest`, {
    method: "POST",
    body: formData,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Error ${res.status}: ${res.statusText}`)
  }

  return res.json()
}
