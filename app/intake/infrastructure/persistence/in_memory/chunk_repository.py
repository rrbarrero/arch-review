from collections.abc import Sequence
from math import sqrt

from app.chat.domain.services.retrieval_service import ScoredChunk
from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.value_objects.status import ChunkStatus


class InMemoryChunkRepository:
    def __init__(self) -> None:
        self._storage: dict[str, DocumentChunk] = {}

    async def save(self, chunk: DocumentChunk) -> None:
        self._storage[chunk.id] = chunk

    async def save_many(self, chunks: Sequence[DocumentChunk]) -> None:
        for chunk in chunks:
            self._storage[chunk.id] = chunk

    async def find_by_id(self, chunk_id: str) -> DocumentChunk | None:
        return self._storage.get(chunk_id)

    async def find_by_document_id(self, document_id: str) -> Sequence[DocumentChunk]:
        return sorted(
            [c for c in self._storage.values() if c.document_id == document_id],
            key=lambda c: c.position,
        )

    async def find_by_status(self, status: ChunkStatus) -> Sequence[DocumentChunk]:
        return [c for c in self._storage.values() if c.status == status]

    async def search_similar(
        self, embedding: list[float], limit: int = 6, level: int | None = None
    ) -> Sequence[ScoredChunk]:
        scored: list[ScoredChunk] = []
        for chunk in self._storage.values():
            if chunk.embedding is None:
                continue
            if level is not None and chunk.level != level:
                continue
            scored.append(
                ScoredChunk(
                    chunk=chunk,
                    filename=chunk.document_id,
                    score=self._cosine_similarity(embedding, chunk.embedding),
                )
            )

        return sorted(scored, key=lambda item: item.score, reverse=True)[:limit]

    async def get_max_level(self) -> int:
        if not self._storage:
            return 0
        return max(c.level for c in self._storage.values())

    async def delete(self, chunk_id: str) -> None:
        self._storage.pop(chunk_id, None)

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        if len(left) != len(right):
            return 0.0

        dot = sum(a * b for a, b in zip(left, right, strict=True))
        left_norm = sqrt(sum(a * a for a in left))
        right_norm = sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)
