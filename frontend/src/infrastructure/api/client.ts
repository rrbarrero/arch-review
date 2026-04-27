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

interface RawIngestDocumentResult {
  document_id: string
  filename: string
  chunk_count: number
}

interface RawIngestDocumentsResponse {
  documents: RawIngestDocumentResult[]
  errors: string[]
}

export interface ChatMessageInput {
  role: "user" | "assistant" | "system"
  content: string
}

export interface ChatCitation {
  documentId: string
  chunkId: string
  filename: string
  snippet: string
  score: number | null
}

export interface ChatResponse {
  text: string
  citations: ChatCitation[]
}

interface RawChatCitation {
  document_id: string
  chunk_id: string
  filename: string
  snippet: string
  score: number | null
}

interface RawChatResponse {
  text: string
  citations: RawChatCitation[]
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

  const result = (await res.json()) as RawIngestDocumentsResponse
  return {
    documents: result.documents.map((document) => ({
      documentId: document.document_id,
      filename: document.filename,
      chunkCount: document.chunk_count,
    })),
    errors: result.errors,
  }
}

export async function askQuestion(
  messages: ChatMessageInput[],
  abortSignal?: AbortSignal,
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
    signal: abortSignal,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Error ${res.status}: ${res.statusText}`)
  }

  const result = (await res.json()) as RawChatResponse
  return {
    text: result.text,
    citations: result.citations.map((citation) => ({
      documentId: citation.document_id,
      chunkId: citation.chunk_id,
      filename: citation.filename,
      snippet: citation.snippet,
      score: citation.score,
    })),
  }
}
