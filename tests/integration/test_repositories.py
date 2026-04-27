from datetime import datetime, timezone

import pytest

from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.entities.document import Document
from app.intake.domain.value_objects import ChunkStatus, Metadata, ProcessingStatus, Source


@pytest.mark.asyncio
async def test_save_and_find_document_by_id(
    in_memory_document_repo,
    pg_document_repo,
    sample_document: Document,
) -> None:
    for repo in [in_memory_document_repo, pg_document_repo]:
        await repo.save(sample_document)
        found = await repo.find_by_id(sample_document.id)
        assert found is not None
        assert found.id == sample_document.id
        assert found.source.filename == "report.pdf"
        assert found.source.content_type == "application/pdf"
        assert found.source.size_bytes == 4096
        assert found.status == ProcessingStatus.PENDING
        assert found.raw_text is None
        assert found.metadata.values == {"department": "engineering"}
        assert found.error is None


@pytest.mark.asyncio
async def test_find_document_by_id_returns_none_when_missing(
    in_memory_document_repo,
    pg_document_repo,
) -> None:
    for repo in [in_memory_document_repo, pg_document_repo]:
        found = await repo.find_by_id("non-existent")
        assert found is None


@pytest.mark.asyncio
async def test_save_updates_existing_document(
    in_memory_document_repo,
    pg_document_repo,
    sample_document: Document,
) -> None:
    for repo in [in_memory_document_repo, pg_document_repo]:
        await repo.save(sample_document)

        sample_document.status = ProcessingStatus.COMPLETED
        sample_document.raw_text = "processed content"
        sample_document.updated_at = datetime.now(timezone.utc)
        await repo.save(sample_document)

        found = await repo.find_by_id(sample_document.id)
        assert found is not None
        assert found.status == ProcessingStatus.COMPLETED
        assert found.raw_text == "processed content"


@pytest.mark.asyncio
async def test_find_documents_by_status(
    in_memory_document_repo,
    pg_document_repo,
) -> None:
    now = datetime.now(timezone.utc)
    docs = [
        Document(id="d1", source=Source("a.pdf", "application/pdf", 100), status=ProcessingStatus.PENDING, raw_text=None, metadata=Metadata(), created_at=now, updated_at=now),
        Document(id="d2", source=Source("b.pdf", "application/pdf", 200), status=ProcessingStatus.COMPLETED, raw_text=None, metadata=Metadata(), created_at=now, updated_at=now),
        Document(id="d3", source=Source("c.pdf", "application/pdf", 300), status=ProcessingStatus.PENDING, raw_text=None, metadata=Metadata(), created_at=now, updated_at=now),
    ]

    for repo in [in_memory_document_repo, pg_document_repo]:
        for d in docs:
            await repo.save(d)

        pending = await repo.find_by_status(ProcessingStatus.PENDING)
        assert len(pending) == 2
        assert {d.id for d in pending} == {"d1", "d3"}

        completed = await repo.find_by_status(ProcessingStatus.COMPLETED)
        assert len(completed) == 1
        assert completed[0].id == "d2"


@pytest.mark.asyncio
async def test_find_documents_by_status_returns_empty_when_no_match(
    in_memory_document_repo,
    pg_document_repo,
) -> None:
    for repo in [in_memory_document_repo, pg_document_repo]:
        result = await repo.find_by_status(ProcessingStatus.FAILED)
        assert result == []


@pytest.mark.asyncio
async def test_delete_document(
    in_memory_document_repo,
    pg_document_repo,
    sample_document: Document,
) -> None:
    for repo in [in_memory_document_repo, pg_document_repo]:
        await repo.save(sample_document)
        assert await repo.find_by_id(sample_document.id) is not None

        await repo.delete(sample_document.id)
        assert await repo.find_by_id(sample_document.id) is None


# --- Chunk repository tests ---


@pytest.mark.asyncio
async def test_save_and_find_chunk_by_id(
    in_memory_document_repo,
    in_memory_chunk_repo,
    pg_document_repo,
    pg_chunk_repo,
    sample_document: Document,
    sample_chunk: DocumentChunk,
) -> None:
    in_memory_chunk_repos = [(in_memory_document_repo, in_memory_chunk_repo)]
    pg_chunk_repos = [(pg_document_repo, pg_chunk_repo)]

    for doc_repo, chunk_repo in [*in_memory_chunk_repos, *pg_chunk_repos]:
        await doc_repo.save(sample_document)
        await chunk_repo.save(sample_chunk)

        found = await chunk_repo.find_by_id(sample_chunk.id)
        assert found is not None
        assert found.id == "chunk-1"
        assert found.document_id == "doc-1"
        assert found.content == "Test chunk content"
        assert found.position == 0
        assert found.status == ChunkStatus.PENDING
        assert found.embedding is None
        assert found.graph_node_id is None
        assert found.error is None


@pytest.mark.asyncio
async def test_save_many_chunks(
    in_memory_document_repo,
    in_memory_chunk_repo,
    pg_document_repo,
    pg_chunk_repo,
) -> None:
    now = datetime.now(timezone.utc)
    doc = Document(id="d-batch", source=Source("batch.pdf", "application/pdf", 500), status=ProcessingStatus.PENDING, raw_text=None, metadata=Metadata(), created_at=now, updated_at=now)
    chunks = [
        DocumentChunk(id="c1", document_id="d-batch", content="first", position=0, status=ChunkStatus.PENDING, metadata=Metadata(), created_at=now),
        DocumentChunk(id="c2", document_id="d-batch", content="second", position=1, status=ChunkStatus.PENDING, metadata=Metadata(), created_at=now),
        DocumentChunk(id="c3", document_id="d-batch", content="third", position=2, status=ChunkStatus.PENDING, metadata=Metadata(), created_at=now),
    ]

    in_memory_pairs = [(in_memory_document_repo, in_memory_chunk_repo)]
    pg_pairs = [(pg_document_repo, pg_chunk_repo)]

    for doc_repo, chunk_repo in [*in_memory_pairs, *pg_pairs]:
        await doc_repo.save(doc)
        await chunk_repo.save_many(chunks)

        found = await chunk_repo.find_by_document_id("d-batch")
        assert len(found) == 3
        assert [c.content for c in found] == ["first", "second", "third"]


@pytest.mark.asyncio
async def test_find_chunks_by_document_id_returns_empty_when_no_chunks(
    in_memory_chunk_repo,
    pg_chunk_repo,
) -> None:
    for repo in [in_memory_chunk_repo, pg_chunk_repo]:
        result = await repo.find_by_document_id("no-chunks")
        assert result == []


@pytest.mark.asyncio
async def test_find_chunks_by_status(
    in_memory_document_repo,
    in_memory_chunk_repo,
    pg_document_repo,
    pg_chunk_repo,
) -> None:
    now = datetime.now(timezone.utc)
    doc = Document(id="d-status", source=Source("s.pdf", "application/pdf", 100), status=ProcessingStatus.PENDING, raw_text=None, metadata=Metadata(), created_at=now, updated_at=now)
    chunks = [
        DocumentChunk(id="cs1", document_id="d-status", content="a", position=0, status=ChunkStatus.PENDING, metadata=Metadata(), created_at=now),
        DocumentChunk(id="cs2", document_id="d-status", content="b", position=1, status=ChunkStatus.EMBEDDED, metadata=Metadata(), created_at=now),
        DocumentChunk(id="cs3", document_id="d-status", content="c", position=2, status=ChunkStatus.PENDING, metadata=Metadata(), created_at=now),
        DocumentChunk(id="cs4", document_id="d-status", content="d", position=3, status=ChunkStatus.GRAPH_PROCESSED, metadata=Metadata(), created_at=now),
    ]

    in_memory_pairs = [(in_memory_document_repo, in_memory_chunk_repo)]
    pg_pairs = [(pg_document_repo, pg_chunk_repo)]

    for doc_repo, chunk_repo in [*in_memory_pairs, *pg_pairs]:
        await doc_repo.save(doc)
        await chunk_repo.save_many(chunks)

        pending = await chunk_repo.find_by_status(ChunkStatus.PENDING)
        assert len(pending) == 2
        assert {c.id for c in pending} == {"cs1", "cs3"}

        embedded = await chunk_repo.find_by_status(ChunkStatus.EMBEDDED)
        assert len(embedded) == 1
        assert embedded[0].id == "cs2"

        graph_processed = await chunk_repo.find_by_status(ChunkStatus.GRAPH_PROCESSED)
        assert len(graph_processed) == 1
        assert graph_processed[0].id == "cs4"


@pytest.mark.asyncio
async def test_delete_chunk(
    in_memory_document_repo,
    in_memory_chunk_repo,
    pg_document_repo,
    pg_chunk_repo,
    sample_document: Document,
    sample_chunk: DocumentChunk,
) -> None:
    in_memory_pairs = [(in_memory_document_repo, in_memory_chunk_repo)]
    pg_pairs = [(pg_document_repo, pg_chunk_repo)]

    for doc_repo, chunk_repo in [*in_memory_pairs, *pg_pairs]:
        await doc_repo.save(sample_document)
        await chunk_repo.save(sample_chunk)
        assert await chunk_repo.find_by_id(sample_chunk.id) is not None

        await chunk_repo.delete(sample_chunk.id)
        assert await chunk_repo.find_by_id(sample_chunk.id) is None


@pytest.mark.asyncio
async def test_cascade_delete_document_removes_chunks_in_postgres(
    pg_document_repo,
    pg_chunk_repo,
) -> None:
    now = datetime.now(timezone.utc)
    doc = Document(id="cascade-doc", source=Source("c.pdf", "application/pdf", 100), status=ProcessingStatus.PENDING, raw_text=None, metadata=Metadata(), created_at=now, updated_at=now)
    chunk = DocumentChunk(id="cascade-chunk", document_id="cascade-doc", content="will be deleted", position=0, status=ChunkStatus.PENDING, metadata=Metadata(), created_at=now)

    await pg_document_repo.save(doc)
    await pg_chunk_repo.save(chunk)
    assert await pg_chunk_repo.find_by_id("cascade-chunk") is not None

    await pg_document_repo.delete("cascade-doc")
    assert await pg_chunk_repo.find_by_id("cascade-chunk") is None


@pytest.mark.asyncio
async def test_get_max_level_after_dict_row_query(
    pg_document_repo,
    pg_chunk_repo,
) -> None:
    now = datetime.now(timezone.utc)
    doc = Document(
        id="level-doc",
        source=Source("levels.py", "text/x-python", 100),
        status=ProcessingStatus.PENDING,
        raw_text=None,
        metadata=Metadata(),
        created_at=now,
        updated_at=now,
    )
    chunk = DocumentChunk(
        id="level-chunk",
        document_id="level-doc",
        content="summary",
        position=0,
        status=ChunkStatus.EMBEDDED,
        metadata=Metadata(),
        created_at=now,
        level=2,
    )

    await pg_document_repo.save(doc)
    await pg_chunk_repo.save(chunk)

    assert await pg_chunk_repo.find_by_id("level-chunk") is not None
    assert await pg_chunk_repo.get_max_level() == 2
