from collections.abc import Sequence

from app.intake.domain.entities.document import Document
from app.intake.domain.value_objects.status import ProcessingStatus


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self._storage: dict[str, Document] = {}

    async def save(self, document: Document) -> None:
        self._storage[document.id] = document

    async def find_by_id(self, document_id: str) -> Document | None:
        return self._storage.get(document_id)

    async def find_by_status(self, status: ProcessingStatus) -> Sequence[Document]:
        return [d for d in self._storage.values() if d.status == status]

    async def delete(self, document_id: str) -> None:
        self._storage.pop(document_id, None)
