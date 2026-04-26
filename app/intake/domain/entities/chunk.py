from dataclasses import dataclass
from datetime import datetime

from app.intake.domain.value_objects.metadata import Metadata
from app.intake.domain.value_objects.status import ChunkStatus


@dataclass
class DocumentChunk:
    id: str
    document_id: str
    content: str
    position: int
    status: ChunkStatus
    metadata: Metadata
    created_at: datetime
    embedding: list[float] | None = None
    graph_node_id: str | None = None
    error: str | None = None
