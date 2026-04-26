from psycopg_pool import AsyncConnectionPool

from app.intake.application.use_cases.ingest_documents import IngestDocumentsUseCase
from app.intake.domain.services.embedding_service import EmbeddingService
from app.intake.infrastructure.external_services.neo4j import Neo4jGraphService
from app.intake.infrastructure.persistence.postgres import (
    PostgresChunkRepository,
    PostgresDocumentRepository,
)


def create_ingest_use_case(pool: AsyncConnectionPool) -> IngestDocumentsUseCase:
    return IngestDocumentsUseCase(
        document_repository=PostgresDocumentRepository(pool),
        chunk_repository=PostgresChunkRepository(pool),
        embedding_service=EmbeddingService(),
        graph_service=Neo4jGraphService(),
    )

