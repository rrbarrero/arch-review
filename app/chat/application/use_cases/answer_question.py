from app.chat.application.dto import ChatCitation, ChatMessageInput, ChatResponse
from app.chat.domain.services import AnswerService, RetrievalService, ScoredChunk


class AnswerQuestionUseCase:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        answer_service: AnswerService | None = None,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._answer_service = answer_service or AnswerService()

    async def execute(self, messages: list[ChatMessageInput]) -> ChatResponse:
        question = self._last_user_message(messages)
        if not question:
            return ChatResponse(text="Ask a question to analyze the ingested documents.")

        context = await self._retrieval_service.retrieve(question)
        answer = await self._answer_service.answer(question, context)

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
