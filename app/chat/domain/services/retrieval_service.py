from dataclasses import dataclass

from opentelemetry import trace

from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.repositories.chunk_repository import ChunkRepository
from app.intake.domain.services.embedding_service import EmbeddingService

tracer = trace.get_tracer(__name__)


@dataclass(frozen=True)
class ScoredChunk:
    chunk: DocumentChunk
    filename: str
    score: float


class RetrievalService:
    def __init__(
        self,
        chunk_repository: ChunkRepository,
        embedding_service: EmbeddingService | None = None,
        limit: int = 6,
    ) -> None:
        self._chunk_repository = chunk_repository
        self._embedding_service = embedding_service or EmbeddingService()
        self._limit = limit

    async def retrieve(self, question: str) -> list[ScoredChunk]:
        with tracer.start_as_current_span("retrieve") as span:
            span.set_attribute("question_length", len(question))
            span.set_attribute("limit", self._limit)
            embedding = await self._embedding_service.embed_query(question)
            span.set_attribute("embedding_dim", len(embedding))

            max_level = await self._chunk_repository.get_max_level()
            span.set_attribute("max_level", max_level)

            if max_level <= 0:
                results = list(await self._chunk_repository.search_similar(embedding, self._limit))
            else:
                results = await self._hierarchical_retrieve(embedding, max_level)

            span.set_attribute("result_count", len(results))
            return results

    async def _hierarchical_retrieve(
        self, embedding: list[float], max_level: int
    ) -> list[ScoredChunk]:
        import asyncio

        levels = list(range(max_level + 1))
        per_level = max(1, self._limit // len(levels))

        tasks = []
        for lvl in reversed(levels):
            slots = per_level if lvl > 0 else self._limit - (per_level * (len(levels) - 1))
            slots = max(1, min(slots, self._limit))
            tasks.append(self._chunk_repository.search_similar(embedding, slots, level=lvl))

        results_per_level = await asyncio.gather(*tasks)

        seen_ids: set[str] = set()
        merged: list[ScoredChunk] = []
        for level_results in results_per_level:
            for r in level_results:
                if r.chunk.id not in seen_ids:
                    merged.append(r)
                    seen_ids.add(r.chunk.id)

        return merged[:self._limit]
