from collections.abc import Sequence

from opentelemetry import trace

from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.value_objects import ChunkStatus
from app.llm import get_embeddings
from app.metrics import chunks_embedded_total

tracer = trace.get_tracer(__name__)


class EmbeddingService:
    async def embed_query(self, text: str) -> list[float]:
        with tracer.start_as_current_span("embed_query") as span:
            span.set_attribute("query_length", len(text))
            result = await get_embeddings().aembed_query(text)
            span.set_attribute("embedding_dim", len(result))
            return result

    async def embed(self, chunks: Sequence[DocumentChunk]) -> list[DocumentChunk]:
        with tracer.start_as_current_span("embed_chunks") as span:
            texts = [c.content for c in chunks]
            span.set_attribute("chunk_count", len(texts))
            embeddings = await get_embeddings().aembed_documents(texts)

            result = list(chunks)
            for i, embedding in enumerate(embeddings):
                result[i].embedding = embedding
                result[i].status = ChunkStatus.EMBEDDED

            span.set_attribute("embedding_dim", len(embeddings[0]) if embeddings else 0)
            chunks_embedded_total.inc(len(chunks))
            return result
