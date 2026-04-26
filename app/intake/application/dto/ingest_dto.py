from dataclasses import dataclass, field


@dataclass
class FileInput:
    filename: str
    content: bytes


@dataclass
class DocumentResult:
    document_id: str
    filename: str
    chunk_count: int


@dataclass
class IngestDocumentsOutput:
    documents: list[DocumentResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
