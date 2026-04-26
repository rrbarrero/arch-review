import pytest

from app.intake.application.dto.ingest_dto import FileInput
from app.intake.application.use_cases.ingest_documents import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    IngestDocumentsUseCase,
)
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
