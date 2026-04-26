from collections.abc import Sequence

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import AsyncConnectionPool

from app.intake.domain.entities.document import Document
from app.intake.domain.value_objects.metadata import Metadata
from app.intake.domain.value_objects.source import Source
from app.intake.domain.value_objects.status import ProcessingStatus


class PostgresDocumentRepository:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    async def save(self, document: Document) -> None:
        async with self._pool.connection() as conn:
            await conn.execute(
                """
                INSERT INTO documents (id, source_filename, source_content_type,
                    source_size_bytes, status, raw_text, metadata, created_at, updated_at, error)
                VALUES (%(id)s, %(source_filename)s, %(source_content_type)s,
                    %(source_size_bytes)s, %(status)s, %(raw_text)s, %(metadata)s,
                    %(created_at)s, %(updated_at)s, %(error)s)
                ON CONFLICT (id) DO UPDATE SET
                    status            = EXCLUDED.status,
                    raw_text          = EXCLUDED.raw_text,
                    metadata          = EXCLUDED.metadata,
                    updated_at        = EXCLUDED.updated_at,
                    error             = EXCLUDED.error
                """,
                {
                    "id": document.id,
                    "source_filename": document.source.filename,
                    "source_content_type": document.source.content_type,
                    "source_size_bytes": document.source.size_bytes,
                    "status": document.status.value,
                    "raw_text": document.raw_text,
                    "metadata": Jsonb(document.metadata.values),
                    "created_at": document.created_at,
                    "updated_at": document.updated_at,
                    "error": document.error,
                },
            )

    async def find_by_id(self, document_id: str) -> Document | None:
        async with self._pool.connection() as conn:
            conn.row_factory = dict_row  # ty: ignore[invalid-assignment]
            row = await conn.execute(
                "SELECT * FROM documents WHERE id = %s",
                (document_id,),
            )
            record = await row.fetchone()
            if record is None:
                return None
            return self._row_to_document(record)  # ty: ignore[invalid-argument-type]

    async def find_by_status(self, status: ProcessingStatus) -> Sequence[Document]:
        async with self._pool.connection() as conn:
            conn.row_factory = dict_row  # ty: ignore[invalid-assignment]
            cur = await conn.execute(
                "SELECT * FROM documents WHERE status = %s ORDER BY created_at",
                (status.value,),
            )
            records = await cur.fetchall()
            return [self._row_to_document(r) for r in records]  # ty: ignore[invalid-argument-type]

    async def delete(self, document_id: str) -> None:
        async with self._pool.connection() as conn:
            await conn.execute(
                "DELETE FROM documents WHERE id = %s",
                (document_id,),
            )

    @staticmethod
    def _row_to_document(row: dict) -> Document:
        return Document(
            id=row["id"],
            source=Source(
                filename=row["source_filename"],
                content_type=row["source_content_type"],
                size_bytes=row["source_size_bytes"],
            ),
            status=ProcessingStatus(row["status"]),
            raw_text=row["raw_text"],
            metadata=Metadata(values=row["metadata"] or {}),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            error=row["error"],
        )
