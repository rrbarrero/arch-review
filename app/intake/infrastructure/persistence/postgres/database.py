import textwrap

from psycopg_pool import AsyncConnectionPool

from app.settings import Settings

SCHEMA_SQL = textwrap.dedent("""\
    CREATE EXTENSION IF NOT EXISTS vector;

    CREATE TABLE IF NOT EXISTS documents (
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

    CREATE TABLE IF NOT EXISTS chunks (
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

    CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
    CREATE INDEX IF NOT EXISTS idx_chunks_status ON chunks(status);
    CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
""")


def create_pool(settings: Settings | None = None) -> AsyncConnectionPool:
    if settings is None:
        settings = Settings()

    return AsyncConnectionPool(
        conninfo=(
            f"host={settings.pgvector_host} "
            f"port={settings.pgvector_port} "
            f"dbname={settings.pgvector_database} "
            f"user={settings.pgvector_user} "
            f"password={settings.pgvector_password}"
        ),
        open=False,
    )


async def ensure_schema(pool: AsyncConnectionPool) -> None:
    async with pool.connection() as conn:
        await conn.execute(SCHEMA_SQL)  # ty: ignore[no-matching-overload]
