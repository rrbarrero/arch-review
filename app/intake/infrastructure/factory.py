import logging

from psycopg_pool import AsyncConnectionPool

from app.intake.application.use_cases.ingest_documents import IngestDocumentsUseCase
from app.intake.domain.services.embedding_service import EmbeddingService
from app.intake.domain.services.raptor_service import RaptorService
from app.intake.infrastructure.external_services.neo4j import Neo4jGraphService
from app.intake.infrastructure.persistence.postgres import (
    PostgresChunkRepository,
    PostgresDocumentRepository,
)
from app.llm import get_llm

logger = logging.getLogger(__name__)


async def _llm_summarize(text: str) -> str:
    llm = get_llm(temperature=0.0)
    prompt = (
        "Summarize the following documentation concisely, "
        "preserving all key technical details, decisions, and code references:\n\n"
        f"{text}"
    )
    response = await llm.ainvoke(prompt)
    content = getattr(response, "content", response)
    return content if isinstance(content, str) else str(content)


def create_ingest_use_case(pool: AsyncConnectionPool) -> IngestDocumentsUseCase:
    try:
        raptor_service = RaptorService(summarizer=_llm_summarize)
        logger.info("RaptorService initialized with LLM summarizer")
    except Exception:
        logger.warning("Failed to create RaptorService, running without RAPTOR")
        raptor_service = None

    return IngestDocumentsUseCase(
        document_repository=PostgresDocumentRepository(pool),
        chunk_repository=PostgresChunkRepository(pool),
        embedding_service=EmbeddingService(),
        graph_service=Neo4jGraphService(),
        raptor_service=raptor_service,
    )

