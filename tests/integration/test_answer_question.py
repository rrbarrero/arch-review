from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.chat.application.dto import ChatMessageInput
from app.chat.application.use_cases import AnswerQuestionUseCase
from app.chat.domain.services import AnswerService, RetrievalService
from app.chat.infrastructure.routers.chat import router as chat_router
from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.value_objects import ChunkStatus, Metadata


class FakeEmbeddingService:
    async def embed_query(self, _text: str) -> list[float]:
        return [1.0, 0.0]


class EchoAnswerService(AnswerService):
    async def answer(self, question, context) -> str:
        filenames = ", ".join(item.filename for item in context)
        return f"{question} -> {filenames}"


def _chunk(
    chunk_id: str,
    document_id: str,
    content: str,
    embedding: list[float] | None,
) -> DocumentChunk:
    return DocumentChunk(
        id=chunk_id,
        document_id=document_id,
        content=content,
        position=0,
        status=ChunkStatus.EMBEDDED,
        metadata=Metadata(),
        created_at=datetime.now(timezone.utc),
        embedding=embedding,
    )


@pytest.mark.asyncio
async def test_answer_question_uses_last_user_message(in_memory_chunk_repo) -> None:
    await in_memory_chunk_repo.save(
        _chunk("chunk-1", "README.md", "FastAPI ingests Markdown documents.", [1.0, 0.0])
    )

    use_case = AnswerQuestionUseCase(
        retrieval_service=RetrievalService(
            in_memory_chunk_repo,
            embedding_service=FakeEmbeddingService(),  # ty: ignore[invalid-argument-type]
        ),
        answer_service=EchoAnswerService(),
    )

    response = await use_case.execute(
        [
            ChatMessageInput(role="user", content="Old question"),
            ChatMessageInput(role="assistant", content="Old answer"),
            ChatMessageInput(role="user", content="What does ingestion do?"),
        ]
    )

    assert response.text == "What does ingestion do? -> README.md"
    assert len(response.citations) == 1
    assert response.citations[0].chunk_id == "chunk-1"
    assert response.citations[0].document_id == "README.md"
    assert response.citations[0].filename == "README.md"


@pytest.mark.asyncio
async def test_answer_question_handles_missing_question(in_memory_chunk_repo) -> None:
    use_case = AnswerQuestionUseCase(
        retrieval_service=RetrievalService(
            in_memory_chunk_repo,
            embedding_service=FakeEmbeddingService(),  # ty: ignore[invalid-argument-type]
        ),
        answer_service=EchoAnswerService(),
    )

    response = await use_case.execute([])

    assert "Ask a question" in response.text
    assert response.citations == []


def test_chat_endpoint_contract(in_memory_chunk_repo) -> None:
    app = FastAPI()
    app.include_router(chat_router)
    app.state.answer_question_use_case = AnswerQuestionUseCase(
        retrieval_service=RetrievalService(
            in_memory_chunk_repo,
            embedding_service=FakeEmbeddingService(),  # ty: ignore[invalid-argument-type]
        ),
        answer_service=EchoAnswerService(),
    )

    client = TestClient(app)
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "Is there context?"}]},
    )

    assert response.status_code == 200
    assert response.json() == {"text": "Is there context? -> ", "citations": []}
