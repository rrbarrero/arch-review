from collections.abc import Sequence

from opentelemetry import trace

from app.chat.domain.services.retrieval_service import ScoredChunk
from app.llm import get_llm

tracer = trace.get_tracer(__name__)


class AnswerService:
    async def answer(self, question: str, context: Sequence[ScoredChunk]) -> str:
        with tracer.start_as_current_span("llm_answer") as span:
            span.set_attribute("question_length", len(question))
            span.set_attribute("context_chunks", len(context))
            if not context:
                return (
                    "There are no ingested documents with embeddings available to answer with "
                    "evidence. Ingest Markdown or Python files first, then ask again."
                )

            prompt = self._build_prompt(question, context)
            span.set_attribute("prompt_length", len(prompt))
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
                f"(document_id={item.chunk.document_id}, chunk_id={item.chunk.id})"
                + (f" [level {item.chunk.level} summary]" if item.chunk.level > 0 else "")
                + "\n"
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
