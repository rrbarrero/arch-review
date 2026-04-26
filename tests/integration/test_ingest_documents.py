import pytest

from app.intake.application.dto.ingest_dto import FileInput
from app.intake.application.use_cases.ingest_documents import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    IngestDocumentsUseCase,
)
from app.intake.domain.services.raptor_service import RaptorService
from app.intake.domain.value_objects import ProcessingStatus


@pytest.fixture
def use_case(in_memory_document_repo, in_memory_chunk_repo) -> IngestDocumentsUseCase:
    return IngestDocumentsUseCase(
        document_repository=in_memory_document_repo,
        chunk_repository=in_memory_chunk_repo,
    )


class TestIngestDocuments:
    def _file(self, name: str, content: str = "hello") -> FileInput:
        return FileInput(filename=name, content=content.encode("utf-8"))

    @pytest.mark.asyncio
    async def test_ingest_single_markdown(self, use_case) -> None:
        files = [self._file("readme.md", "# Title\n\nSome text here.")]
        output = await use_case.execute(files)

        assert len(output.documents) == 1
        assert output.errors == []
        assert output.documents[0].filename == "readme.md"

        doc_id = output.documents[0].document_id
        doc = await use_case._document_repository.find_by_id(doc_id)
        assert doc is not None
        assert doc.source.filename == "readme.md"
        assert doc.source.content_type == "text/markdown"
        assert doc.source.size_bytes == 24
        assert doc.status == ProcessingStatus.PENDING
        assert doc.raw_text == "# Title\n\nSome text here."

        chunks = await use_case._chunk_repository.find_by_document_id(doc_id)
        assert len(chunks) >= 1
        assert chunks[0].position == 0

    @pytest.mark.asyncio
    async def test_ingest_single_python(self, use_case) -> None:
        files = [self._file("script.py", "def foo():\n    pass\n\ndef bar():\n    return 1")]
        output = await use_case.execute(files)

        assert len(output.documents) == 1
        assert output.errors == []
        assert output.documents[0].filename == "script.py"

        doc_id = output.documents[0].document_id
        doc = await use_case._document_repository.find_by_id(doc_id)
        assert doc.source.content_type == "text/x-python"

    @pytest.mark.asyncio
    async def test_ingest_multiple_files(self, use_case) -> None:
        files = [
            self._file("a.md", "# A"),
            self._file("b.py", "x = 1"),
            self._file("c.md", "# C"),
        ]
        output = await use_case.execute(files)

        assert len(output.documents) == 3
        assert output.errors == []
        assert [d.filename for d in output.documents] == ["a.md", "b.py", "c.md"]

    @pytest.mark.asyncio
    async def test_reject_unsupported_extension(self, use_case) -> None:
        files = [self._file("data.pdf", "fake pdf content")]
        output = await use_case.execute(files)

        assert output.documents == []
        assert len(output.errors) == 1
        assert "data.pdf" in output.errors[0]
        assert ALLOWED_EXTENSIONS.isdisjoint({".pdf"})

    @pytest.mark.asyncio
    async def test_reject_file_too_large(self, use_case) -> None:
        oversized = "x" * (MAX_FILE_SIZE + 1)
        files = [self._file("big.md", oversized)]
        output = await use_case.execute(files)

        assert output.documents == []
        assert len(output.errors) == 1
        assert "big.md" in output.errors[0]
        assert "too large" in output.errors[0]

    @pytest.mark.asyncio
    async def test_partial_failure(self, use_case) -> None:
        oversized = "x" * (MAX_FILE_SIZE + 1)
        files = [
            self._file("good.md", "fine"),
            self._file("bad.pdf", "not allowed"),
            self._file("big.py", oversized),
        ]
        output = await use_case.execute(files)

        assert len(output.documents) == 1
        assert len(output.errors) == 2
        assert output.documents[0].filename == "good.md"

    @pytest.mark.asyncio
    async def test_empty_file(self, use_case) -> None:
        files = [self._file("empty.md", "")]
        output = await use_case.execute(files)

        assert len(output.documents) == 1
        assert output.errors == []
        assert output.documents[0].chunk_count == 0

    @pytest.mark.asyncio
    async def test_empty_file_list(self, use_case) -> None:
        output = await use_case.execute([])
        assert output.documents == []
        assert output.errors == []


class TestRaptorIngest:
    @pytest.fixture
    def raptor_use_case(
        self, in_memory_document_repo, in_memory_chunk_repo
    ) -> IngestDocumentsUseCase:
        return IngestDocumentsUseCase(
            document_repository=in_memory_document_repo,
            chunk_repository=in_memory_chunk_repo,
            raptor_service=RaptorService(cluster_size=2),
        )

    def _file(self, name: str, content: str = "") -> FileInput:
        return FileInput(filename=name, content=content.encode("utf-8"))

    @staticmethod
    def _large_text() -> str:
        return "\n\n".join(f"Paragraph {i}. " + "word " * 200 for i in range(6))

    @pytest.mark.asyncio
    async def test_raptor_adds_summary_chunks(self, raptor_use_case) -> None:
        files = [self._file("doc.md", self._large_text())]
        output = await raptor_use_case.execute(files)

        assert len(output.documents) == 1
        assert output.errors == []

        doc_id = output.documents[0].document_id
        chunks = await raptor_use_case._chunk_repository.find_by_document_id(doc_id)

        leaf_chunks = [c for c in chunks if c.level == 0]
        summary_chunks = [c for c in chunks if c.level > 0]

        assert len(leaf_chunks) >= 1
        assert len(summary_chunks) >= 1

        for sc in summary_chunks:
            assert sc.level > 0
            assert len(sc.parent_ids) > 0

    @pytest.mark.asyncio
    async def test_raptor_builds_tree_hierarchy(self, raptor_use_case) -> None:
        files = [self._file("data.md", self._large_text())]
        output = await raptor_use_case.execute(files)

        doc_id = output.documents[0].document_id
        chunks = await raptor_use_case._chunk_repository.find_by_document_id(doc_id)

        levels = {c.level for c in chunks}
        assert len(levels) > 1

        top_level = max(levels)
        top_chunks = [c for c in chunks if c.level == top_level]
        assert len(top_chunks) == 1

    @pytest.mark.asyncio
    async def test_raptor_preserves_leaf_chunks(self, raptor_use_case) -> None:
        files = [self._file("doc.md", "# A\n\n# B\n\n# C")]
        output = await raptor_use_case.execute(files)

        doc_id = output.documents[0].document_id
        chunks = await raptor_use_case._chunk_repository.find_by_document_id(doc_id)

        leaves = [c for c in chunks if c.level == 0]
        assert len(leaves) >= 1
        for c in leaves:
            assert c.level == 0
            assert c.parent_ids == ()

    @pytest.mark.asyncio
    async def test_raptor_single_chunk_no_summaries(self, raptor_use_case) -> None:
        files = [self._file("tiny.md", "Just one paragraph.")]
        output = await raptor_use_case.execute(files)

        doc_id = output.documents[0].document_id
        chunks = await raptor_use_case._chunk_repository.find_by_document_id(doc_id)

        assert all(c.level == 0 for c in chunks)

    @pytest.mark.asyncio
    async def test_without_raptor_produces_only_leaves(self, use_case) -> None:
        content = "\n\n".join(f"P{i}." for i in range(10))
        files = [self._file("doc.md", content)]
        output = await use_case.execute(files)

        doc_id = output.documents[0].document_id
        chunks = await use_case._chunk_repository.find_by_document_id(doc_id)

        assert all(c.level == 0 for c in chunks)
