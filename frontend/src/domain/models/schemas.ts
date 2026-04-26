import { z } from "zod"

export const ProcessingStatus = z.enum(["pending", "processing", "completed", "failed"])
export type ProcessingStatus = z.infer<typeof ProcessingStatus>

export const ChunkStatus = z.enum(["pending", "embedded", "graph_processed", "failed"])
export type ChunkStatus = z.infer<typeof ChunkStatus>

export const Source = z.object({
  filename: z.string(),
  contentType: z.string(),
  sizeBytes: z.number(),
})
export type Source = z.infer<typeof Source>

export const Document = z.object({
  id: z.string(),
  source: Source,
  status: ProcessingStatus,
  rawText: z.string().nullable(),
  metadata: z.record(z.unknown()),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  error: z.string().nullable(),
})
export type Document = z.infer<typeof Document>

export const DocumentChunk = z.object({
  id: z.string(),
  documentId: z.string(),
  content: z.string(),
  position: z.number(),
  status: ChunkStatus,
  metadata: z.record(z.unknown()),
  createdAt: z.string().datetime(),
  level: z.number().default(0),
  parentIds: z.array(z.string()).default([]),
  embedding: z.array(z.number()).nullable(),
  graphNodeId: z.string().nullable(),
  error: z.string().nullable(),
})
export type DocumentChunk = z.infer<typeof DocumentChunk>

export const IngestDocumentResult = z.object({
  documentId: z.string(),
  filename: z.string(),
  chunkCount: z.number(),
})
export type IngestDocumentResult = z.infer<typeof IngestDocumentResult>

export const IngestDocumentsResponse = z.object({
  documents: z.array(IngestDocumentResult),
  errors: z.array(z.string()),
})
export type IngestDocumentsResponse = z.infer<typeof IngestDocumentsResponse>
