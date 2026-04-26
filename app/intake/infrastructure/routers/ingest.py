from fastapi import APIRouter, HTTPException, UploadFile

from app.intake.application.dto.ingest_dto import FileInput
from app.intake.application.use_cases.ingest_documents import IngestDocumentsUseCase
from app.intake.infrastructure.persistence.in_memory import (
    InMemoryChunkRepository,
    InMemoryDocumentRepository,
)

router = APIRouter(prefix="/intake", tags=["intake"])


def _default_use_case() -> IngestDocumentsUseCase:
    return IngestDocumentsUseCase(
        document_repository=InMemoryDocumentRepository(),
        chunk_repository=InMemoryChunkRepository(),
    )


@router.post("/ingest")
async def ingest_files(files: list[UploadFile]) -> dict:
    use_case = _default_use_case()
    file_inputs: list[FileInput] = []

    for f in files:
        content = await f.read()
        file_inputs.append(FileInput(filename=f.filename or "unknown", content=content))

    if not file_inputs:
        raise HTTPException(status_code=400, detail="No files provided")

    output = await use_case.execute(file_inputs)
    return {
        "documents": [
            {"document_id": d.document_id, "filename": d.filename, "chunk_count": d.chunk_count}
            for d in output.documents
        ],
        "errors": output.errors,
    }
