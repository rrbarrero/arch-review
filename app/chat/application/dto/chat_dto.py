from pydantic import BaseModel, Field


class ChatMessageInput(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessageInput] = Field(default_factory=list)


class ChatCitation(BaseModel):
    document_id: str
    chunk_id: str
    filename: str
    snippet: str
    score: float | None = None


class ChatResponse(BaseModel):
    text: str
    citations: list[ChatCitation] = Field(default_factory=list)
