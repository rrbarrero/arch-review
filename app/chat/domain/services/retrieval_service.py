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
            results = list(await self._chunk_repository.search_similar(embedding, self._limit))
            span.set_attribute("result_count", len(results))
            return results
