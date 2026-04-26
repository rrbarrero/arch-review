from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.entities.document import Document
from app.intake.domain.value_objects import ChunkStatus, Metadata, ProcessingStatus, Source
from app.intake.infrastructure.persistence.in_memory import (
    InMemoryChunkRepository,
    InMemoryDocumentRepository,
)
from app.intake.infrastructure.persistence.postgres import (
    PostgresChunkRepository,
    PostgresDocumentRepository,
    create_pool,
    ensure_schema,
)


@pytest.fixture
def in_memory_document_repo() -> InMemoryDocumentRepository:
    return InMemoryDocumentRepository()


@pytest.fixture
def in_memory_chunk_repo() -> InMemoryChunkRepository:
    return InMemoryChunkRepository()


@pytest_asyncio.fixture(scope="session")
async def pg_pool() -> AsyncGenerator[AsyncConnectionPool, None]:
    pool = create_pool()
    await pool.open()
    await ensure_schema(pool)
    yield pool
    async with pool.connection() as conn:
        await conn.execute("DROP TABLE IF EXISTS chunks, documents CASCADE")
    await pool.close()


@pytest_asyncio.fixture
async def pg_document_repo(pg_pool: AsyncConnectionPool) -> PostgresDocumentRepository:
    async with pg_pool.connection() as conn:
        await conn.execute("TRUNCATE TABLE chunks, documents CASCADE")
    return PostgresDocumentRepository(pg_pool)


@pytest_asyncio.fixture
async def pg_chunk_repo(pg_pool: AsyncConnectionPool) -> PostgresChunkRepository:
    async with pg_pool.connection() as conn:
        await conn.execute("TRUNCATE TABLE chunks, documents CASCADE")
    return PostgresChunkRepository(pg_pool)


@pytest.fixture
def sample_document() -> Document:
    return Document(
        id="doc-1",
        source=Source(filename="report.pdf", content_type="application/pdf", size_bytes=4096),
        status=ProcessingStatus.PENDING,
        raw_text=None,
        metadata=Metadata({"department": "engineering"}),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_chunk() -> DocumentChunk:
    return DocumentChunk(
        id="chunk-1",
        document_id="doc-1",
        content="Test chunk content",
        position=0,
        status=ChunkStatus.PENDING,
        metadata=Metadata(),
        created_at=datetime.now(timezone.utc),
    )
