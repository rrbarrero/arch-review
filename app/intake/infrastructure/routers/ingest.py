from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.requests import Request

from app.intake.application.dto.ingest_dto import FileInput
from app.intake.application.use_cases.ingest_documents import IngestDocumentsUseCase

router = APIRouter(prefix="/intake", tags=["intake"])


def _get_use_case(request: Request) -> IngestDocumentsUseCase:
    return request.app.state.ingest_use_case


@router.post("/ingest")
async def ingest_files(
    files: list[UploadFile],
    use_case: IngestDocumentsUseCase = Depends(_get_use_case),
) -> dict:
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
