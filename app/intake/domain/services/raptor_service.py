import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from opentelemetry import trace

from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.value_objects import ChunkStatus, Metadata

tracer = trace.get_tracer(__name__)


class RaptorService:
    CLUSTER_SIZE = 5

    def __init__(self, cluster_size: int = 0) -> None:
        self._cluster_size = cluster_size or self.CLUSTER_SIZE

    def build_tree(self, leaf_chunks: Sequence[DocumentChunk], document_id: str) -> list[DocumentChunk]:
        with tracer.start_as_current_span("raptor_build_tree") as span:
            span.set_attribute("document_id", document_id)
            span.set_attribute("leaf_count", len(leaf_chunks))
            all_chunks = list(leaf_chunks)
            current_level = leaf_chunks
            now = datetime.now(timezone.utc)

            while len(current_level) > 1:
                clusters = self._cluster(current_level)
                summaries: list[DocumentChunk] = []

                for parent_ids, cluster_content in clusters:
                    summary = self._summarize(
                        document_id=document_id,
                        content=cluster_content,
                        parent_ids=parent_ids,
                        level=current_level[0].level + 1 if current_level else 1,
                        now=now,
                    )
                    summaries.append(summary)

                all_chunks.extend(summaries)
                current_level = summaries

            span.set_attribute("total_chunks", len(all_chunks))
            span.set_attribute("tree_levels", current_level[0].level if current_level else 0)
            return all_chunks

    def _cluster(self, chunks: Sequence[DocumentChunk]) -> list[tuple[tuple[str, ...], str]]:
        clusters: list[tuple[tuple[str, ...], str]] = []
        for i in range(0, len(chunks), self._cluster_size):
            batch = chunks[i : i + self._cluster_size]
            ids = tuple(c.id for c in batch)
            content = "\n\n".join(c.content for c in batch)
            clusters.append((ids, content))
        return clusters

    @staticmethod
    def _summarize(
        document_id: str,
        content: str,
        parent_ids: tuple[str, ...],
        level: int,
        now: datetime,
    ) -> DocumentChunk:
        return DocumentChunk(
            id=uuid.uuid4().hex,
            document_id=document_id,
            content=content,
            position=0,
            status=ChunkStatus.PENDING,
            metadata=Metadata({"raptor_level": level}),
            created_at=now,
            level=level,
            parent_ids=parent_ids,
        )
