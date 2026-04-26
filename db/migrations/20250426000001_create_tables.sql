-- migrate:up
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id              TEXT PRIMARY KEY,
    source_filename TEXT NOT NULL,
    source_content_type TEXT NOT NULL,
    source_size_bytes  BIGINT NOT NULL,
    status          TEXT NOT NULL,
    raw_text        TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL,
    error           TEXT
);

CREATE TABLE chunks (
    id              TEXT PRIMARY KEY,
    document_id     TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content         TEXT NOT NULL,
    position        INT NOT NULL,
    status          TEXT NOT NULL,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL,
    embedding       vector,
    graph_node_id   TEXT,
    error           TEXT
);

CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_chunks_status ON chunks(status);
CREATE INDEX idx_documents_status ON documents(status);

-- migrate:down
DROP TABLE IF EXISTS chunks;
DROP TABLE IF EXISTS documents;
