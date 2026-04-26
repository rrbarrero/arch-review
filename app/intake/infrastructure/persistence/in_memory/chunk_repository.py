from collections.abc import Sequence

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

    async def delete(self, chunk_id: str) -> None:
        self._storage.pop(chunk_id, None)
