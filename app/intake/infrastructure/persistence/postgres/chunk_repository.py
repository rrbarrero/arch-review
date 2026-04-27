from collections.abc import Sequence
from typing import Any, cast

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import AsyncConnectionPool

from app.chat.domain.services.retrieval_service import ScoredChunk
from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.value_objects.metadata import Metadata
from app.intake.domain.value_objects.status import ChunkStatus


class PostgresChunkRepository:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    async def save(self, chunk: DocumentChunk) -> None:
        async with self._pool.connection() as conn:
            await conn.execute(
                """
                INSERT INTO chunks (id, document_id, content, position, status,
                    metadata, created_at, embedding, graph_node_id, error)
                VALUES (%(id)s, %(document_id)s, %(content)s, %(position)s,
                    %(status)s, %(metadata)s, %(created_at)s, %(embedding)s,
                    %(graph_node_id)s, %(error)s)
                ON CONFLICT (id) DO UPDATE SET
                    status        = EXCLUDED.status,
                    content       = EXCLUDED.content,
                    position      = EXCLUDED.position,
                    metadata      = EXCLUDED.metadata,
                    embedding     = EXCLUDED.embedding,
                    graph_node_id = EXCLUDED.graph_node_id,
                    error         = EXCLUDED.error
                """,
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "position": chunk.position,
                    "status": chunk.status.value,
                    "metadata": Jsonb(chunk.metadata.values),
                    "created_at": chunk.created_at,
                    "embedding": chunk.embedding,
                    "graph_node_id": chunk.graph_node_id,
                    "error": chunk.error,
                },
            )

    async def save_many(self, chunks: Sequence[DocumentChunk]) -> None:
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                for chunk in chunks:
                    await cur.execute(
                        """
                        INSERT INTO chunks (id, document_id, content, position, status,
                            metadata, created_at, embedding, graph_node_id, error)
                        VALUES (%(id)s, %(document_id)s, %(content)s, %(position)s,
                            %(status)s, %(metadata)s, %(created_at)s, %(embedding)s,
                            %(graph_node_id)s, %(error)s)
                        ON CONFLICT (id) DO UPDATE SET
                            status        = EXCLUDED.status,
                            content       = EXCLUDED.content,
                            position      = EXCLUDED.position,
                            metadata      = EXCLUDED.metadata,
                            embedding     = EXCLUDED.embedding,
                            graph_node_id = EXCLUDED.graph_node_id,
                            error         = EXCLUDED.error
                        """,
                        {
                            "id": chunk.id,
                            "document_id": chunk.document_id,
                            "content": chunk.content,
                            "position": chunk.position,
                            "status": chunk.status.value,
                            "metadata": Jsonb(chunk.metadata.values),
                            "created_at": chunk.created_at,
                            "embedding": chunk.embedding,
                            "graph_node_id": chunk.graph_node_id,
                            "error": chunk.error,
                        },
                    )

    async def find_by_id(self, chunk_id: str) -> DocumentChunk | None:
        async with self._pool.connection() as conn:
            conn.row_factory = dict_row  # ty: ignore[invalid-assignment]
            row = await conn.execute(
                "SELECT * FROM chunks WHERE id = %s",
                (chunk_id,),
            )
            record = await row.fetchone()
            if record is None:
                return None
            return self._row_to_chunk(record)  # ty: ignore[invalid-argument-type]

    async def find_by_document_id(self, document_id: str) -> Sequence[DocumentChunk]:
        async with self._pool.connection() as conn:
            conn.row_factory = dict_row  # ty: ignore[invalid-assignment]
            cur = await conn.execute(
                "SELECT * FROM chunks WHERE document_id = %s ORDER BY position",
                (document_id,),
            )
            records = await cur.fetchall()
            return [self._row_to_chunk(r) for r in records]  # ty: ignore[invalid-argument-type]

    async def find_by_status(self, status: ChunkStatus) -> Sequence[DocumentChunk]:
        async with self._pool.connection() as conn:
            conn.row_factory = dict_row  # ty: ignore[invalid-assignment]
            cur = await conn.execute(
                "SELECT * FROM chunks WHERE status = %s ORDER BY created_at",
                (status.value,),
            )
            records = await cur.fetchall()
            return [self._row_to_chunk(r) for r in records]  # ty: ignore[invalid-argument-type]

    async def search_similar(
        self, embedding: list[float], limit: int = 6
    ) -> Sequence[ScoredChunk]:
        async with self._pool.connection() as conn:
            conn.row_factory = dict_row  # ty: ignore[invalid-assignment]
            vector = self._vector_literal(embedding)
            cur = await conn.execute(
                """
                SELECT c.*, d.source_filename,
                    1 - (c.embedding <=> %s::vector) AS score
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE c.embedding IS NOT NULL
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s
                """,
                (vector, vector, limit),
            )
            records = cast(list[dict[str, Any]], await cur.fetchall())
            return [
                ScoredChunk(
                    chunk=self._row_to_chunk(r),
                    filename=r["source_filename"],
                    score=float(r["score"]),
                )
                for r in records
            ]

    async def delete(self, chunk_id: str) -> None:
        async with self._pool.connection() as conn:
            await conn.execute(
                "DELETE FROM chunks WHERE id = %s",
                (chunk_id,),
            )

    @staticmethod
    def _row_to_chunk(row: dict[str, Any]) -> DocumentChunk:
        return DocumentChunk(
            id=row["id"],
            document_id=row["document_id"],
            content=row["content"],
            position=row["position"],
            status=ChunkStatus(row["status"]),
            metadata=Metadata(values=row["metadata"] or {}),
            created_at=row["created_at"],
            embedding=row["embedding"],
            graph_node_id=row["graph_node_id"],
            error=row["error"],
        )

    @staticmethod
    def _vector_literal(embedding: list[float]) -> str:
        return "[" + ",".join(str(value) for value in embedding) + "]"
