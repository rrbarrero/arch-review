from psycopg_pool import AsyncConnectionPool

from app.chat.application.use_cases import AnswerQuestionUseCase
from app.chat.domain.services import AnswerService, RetrievalService
from app.intake.domain.services import EmbeddingService
from app.intake.infrastructure.persistence.postgres import PostgresChunkRepository


def create_answer_question_use_case(pool: AsyncConnectionPool) -> AnswerQuestionUseCase:
    return AnswerQuestionUseCase(
        retrieval_service=RetrievalService(
            chunk_repository=PostgresChunkRepository(pool),
            embedding_service=EmbeddingService(),
        ),
        answer_service=AnswerService(),
    )
