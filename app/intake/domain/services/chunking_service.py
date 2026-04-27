import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from opentelemetry import trace

from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.services.strategies import (
    ChunkingStrategy,
    MarkdownChunkingStrategy,
    PythonChunkingStrategy,
    TypeScriptChunkingStrategy,
)
from app.intake.domain.value_objects import ChunkStatus, Metadata

tracer = trace.get_tracer(__name__)


class _ParagraphFallbackStrategy:
    MAX_CHUNK_SIZE = 1000

    def chunk(self, text: str) -> list[str]:
        segments: list[str] = []
        for paragraph in text.split("\n\n"):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            if len(paragraph) <= self.MAX_CHUNK_SIZE:
                segments.append(paragraph)
            else:
                segments.extend(
                    line.strip() for line in paragraph.splitlines() if line.strip()
                )
        return segments


_CONTENT_TYPE_MAP: dict[str, ChunkingStrategy] = {
    "text/markdown": MarkdownChunkingStrategy(),
    "text/x-python": PythonChunkingStrategy(),
    "text/x-typescript": TypeScriptChunkingStrategy(),
}


class ChunkingService:
    def __init__(self, strategies: dict[str, ChunkingStrategy] | None = None) -> None:
        self._strategies = strategies or _CONTENT_TYPE_MAP
        self._fallback = _ParagraphFallbackStrategy()

    def chunk(self, document_id: str, content: str, content_type: str = "") -> Sequence[DocumentChunk]:
        with tracer.start_as_current_span("chunk") as span:
            span.set_attribute("document_id", document_id)
            span.set_attribute("content_type", content_type)
            span.set_attribute("content_length", len(content))
            strategy = self._strategies.get(content_type, self._fallback)
            segments = strategy.chunk(content)
            now = datetime.now(timezone.utc)

            chunks = [
                self._build_chunk(document_id, i, segment, now)
                for i, segment in enumerate(segments)
            ]
            span.set_attribute("chunk_count", len(chunks))
            return chunks

    @staticmethod
    def _build_chunk(
        document_id: str, position: int, content: str, created_at: datetime
    ) -> DocumentChunk:
        return DocumentChunk(
            id=uuid.uuid4().hex,
            document_id=document_id,
            content=content,
            position=position,
            status=ChunkStatus.PENDING,
            metadata=Metadata(),
            created_at=created_at,
        )
