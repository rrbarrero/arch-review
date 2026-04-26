import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.value_objects import ChunkStatus, Metadata


class ChunkingService:
    MAX_CHUNK_SIZE = 1000

    def chunk(self, document_id: str, content: str) -> Sequence[DocumentChunk]:
        segments = self._split_segments(content)
        now = datetime.now(timezone.utc)

        return [
            self._build_chunk(document_id, i, segment, now)
            for i, segment in enumerate(segments)
        ]

    def _split_segments(self, content: str) -> list[str]:
        segments: list[str] = []
        for paragraph in content.split("\n\n"):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            if len(paragraph) <= self.MAX_CHUNK_SIZE:
                segments.append(paragraph)
            else:
                segments.extend(self._split_long_paragraph(paragraph))
        return segments

    @staticmethod
    def _split_long_paragraph(paragraph: str) -> list[str]:
        return [line.strip() for line in paragraph.splitlines() if line.strip()]

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
