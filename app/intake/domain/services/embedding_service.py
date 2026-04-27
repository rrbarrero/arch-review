from collections.abc import Sequence

from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.value_objects import ChunkStatus
from app.llm import get_embeddings


class EmbeddingService:
    async def embed_query(self, text: str) -> list[float]:
        return await get_embeddings().aembed_query(text)

    async def embed(self, chunks: Sequence[DocumentChunk]) -> list[DocumentChunk]:
        texts = [c.content for c in chunks]
        embeddings = await get_embeddings().aembed_documents(texts)

        result = list(chunks)
        for i, embedding in enumerate(embeddings):
            result[i].embedding = embedding
            result[i].status = ChunkStatus.EMBEDDED

        return result
