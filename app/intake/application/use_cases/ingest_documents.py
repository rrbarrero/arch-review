import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone

from app.intake.application.dto.ingest_dto import (
    DocumentResult,
    FileInput,
    IngestDocumentsOutput,
)
from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.entities.document import Document
from app.intake.domain.repositories.chunk_repository import ChunkRepository
from app.intake.domain.repositories.document_repository import DocumentRepository
from app.intake.domain.services.chunking_service import ChunkingService
from app.intake.domain.services.embedding_service import EmbeddingService
from app.intake.domain.services.raptor_service import RaptorService
from app.intake.domain.value_objects import Metadata, ProcessingStatus, Source
from app.intake.infrastructure.external_services.neo4j import Neo4jGraphService

MAX_FILE_SIZE = 500 * 1024
ALLOWED_EXTENSIONS = {".md", ".py"}


def _extension(filename: str) -> str:
    dot = filename.rfind(".")
    return filename[dot:].lower() if dot != -1 else ""


def _content_type(ext: str) -> str:
    return {"md": "text/markdown", "py": "text/x-python"}.get(ext, "application/octet-stream")


@dataclass
class _ProcessResult:
    document: Document
    chunks: Sequence[DocumentChunk]


class IngestDocumentsUseCase:
    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        chunking_service: ChunkingService | None = None,
        raptor_service: RaptorService | None = None,
        embedding_service: EmbeddingService | None = None,
        graph_service: Neo4jGraphService | None = None,
    ) -> None:
        self._document_repository = document_repository
        self._chunk_repository = chunk_repository
        self._chunking_service = chunking_service or ChunkingService()
        self._raptor_service = raptor_service
        self._embedding_service = embedding_service
        self._graph_service = graph_service

    async def execute(self, files: Sequence[FileInput]) -> IngestDocumentsOutput:
        output = IngestDocumentsOutput()

        for file_input in files:
            error = self._validate(file_input)
            if error:
                output.errors.append(error)
                continue

            result = self._process_file(file_input)

            try:
                result = await self._enrich(result)
            except Exception as e:
                output.errors.append(f"{file_input.filename}: enrichment failed: {e}")
                continue

            await self._persist(result)
            output.documents.append(self._to_result(result))

        return output

    def _validate(self, file: FileInput) -> str | None:
        ext = _extension(file.filename)
        if ext not in ALLOWED_EXTENSIONS:
            return f"{file.filename}: unsupported extension '{ext}'"

        size = len(file.content)
        if size > MAX_FILE_SIZE:
            return f"{file.filename}: file too large ({size} bytes, max {MAX_FILE_SIZE})"

        return None

    def _process_file(self, file: FileInput) -> _ProcessResult:
        ext = _extension(file.filename)
        now = datetime.now(timezone.utc)
        text = file.content.decode("utf-8")

        document = Document(
            id=uuid.uuid4().hex,
            source=Source(
                filename=file.filename,
                content_type=_content_type(ext.lstrip(".")),
                size_bytes=len(file.content),
            ),
            status=ProcessingStatus.PENDING,
            raw_text=text,
            metadata=Metadata(),
            created_at=now,
            updated_at=now,
        )

        chunks: Sequence[DocumentChunk] = self._chunking_service.chunk(
            document.id, text, document.source.content_type
        )

        if self._raptor_service and chunks:
            chunks = self._raptor_service.build_tree(list(chunks), document.id)

        return _ProcessResult(document=document, chunks=list(chunks))

    async def _enrich(self, result: _ProcessResult) -> _ProcessResult:
        chunks = list(result.chunks)

        if self._embedding_service and chunks:
            chunks = await self._embedding_service.embed(chunks)

        if self._graph_service and chunks:
            chunks = await self._graph_service.create_nodes(chunks, result.document.id)

        return _ProcessResult(document=result.document, chunks=chunks)

    async def _persist(self, result: _ProcessResult) -> None:
        await self._document_repository.save(result.document)
        if result.chunks:
            await self._chunk_repository.save_many(result.chunks)

    @staticmethod
    def _to_result(result: _ProcessResult) -> DocumentResult:
        return DocumentResult(
            document_id=result.document.id,
            filename=result.document.source.filename,
            chunk_count=len(result.chunks),
        )
