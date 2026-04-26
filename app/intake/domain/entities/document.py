from dataclasses import dataclass
from datetime import datetime

from app.intake.domain.value_objects.metadata import Metadata
from app.intake.domain.value_objects.source import Source
from app.intake.domain.value_objects.status import ProcessingStatus


@dataclass
class Document:
    id: str
    source: Source
    status: ProcessingStatus
    raw_text: str | None
    metadata: Metadata
    created_at: datetime
    updated_at: datetime
    error: str | None = None
