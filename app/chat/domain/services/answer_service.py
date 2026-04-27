from collections.abc import Sequence

from app.chat.domain.services.retrieval_service import ScoredChunk
from app.llm import get_llm


class AnswerService:
    async def answer(self, question: str, context: Sequence[ScoredChunk]) -> str:
        if not context:
            return (
                "There are no ingested documents with embeddings available to answer with "
                "evidence. Ingest Markdown or Python files first, then ask again."
            )

        prompt = self._build_prompt(question, context)
        response = await get_llm().ainvoke(prompt)
        content = getattr(response, "content", response)
        if isinstance(content, str):
            return content
        return str(content)

    @staticmethod
    def _build_prompt(question: str, context: Sequence[ScoredChunk]) -> str:
        context_blocks = "\n\n".join(
            (
                f"Source {i}: {item.filename} "
                f"(document_id={item.chunk.document_id}, chunk_id={item.chunk.id})\n"
                f"{item.chunk.content}"
            )
            for i, item in enumerate(context, start=1)
        )

        return (
            "You are Arch Review, an architecture review assistant. "
            "Answer only from the evidence in the provided context. "
            "If the context is not sufficient, say that clearly. "
            "Include brief references to the source filenames you used.\n\n"
            f"User question:\n{question}\n\n"
            f"Retrieved context:\n{context_blocks}\n\n"
            "Answer:"
        )
