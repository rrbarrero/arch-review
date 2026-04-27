import logging

from opentelemetry import trace

from app.chat.application.dto import ChatCitation, ChatMessageInput, ChatResponse
from app.chat.domain.services import AnswerService, RetrievalService, ScoredChunk
from app.metrics import context_chunks_retrieved, questions_answered_total

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class AnswerQuestionUseCase:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        answer_service: AnswerService | None = None,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._answer_service = answer_service or AnswerService()

    async def execute(self, messages: list[ChatMessageInput]) -> ChatResponse:
        with tracer.start_as_current_span("answer_question") as span:
            question = self._last_user_message(messages)
            span.set_attribute("question_length", len(question))
            if not question:
                return ChatResponse(text="Ask a question to analyze the ingested documents.")

            context = await self._retrieval_service.retrieve(question)
            span.set_attribute("context_chunks", len(context))
            context_chunks_retrieved.observe(len(context))

            answer = await self._answer_service.answer(question, context)
            span.set_attribute("answer_length", len(answer))

            questions_answered_total.inc()

            logger.info(
                "question_answered",
                extra={"chunks_used": len(context), "answer_length": len(answer)},
            )

            return ChatResponse(
                text=answer,
                citations=[self._to_citation(item) for item in context],
            )

    @staticmethod
    def _last_user_message(messages: list[ChatMessageInput]) -> str:
        for message in reversed(messages):
            if message.role == "user":
                return message.content.strip()
        return ""

    @staticmethod
    def _to_citation(item: ScoredChunk) -> ChatCitation:
        snippet = item.chunk.content[:240].strip()
        if len(item.chunk.content) > len(snippet):
            snippet = f"{snippet}..."

        return ChatCitation(
            document_id=item.chunk.document_id,
            chunk_id=item.chunk.id,
            filename=item.filename,
            snippet=snippet,
            score=item.score,
        )
