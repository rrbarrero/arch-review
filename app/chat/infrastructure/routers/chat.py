from fastapi import APIRouter, Depends
from fastapi.requests import Request

from app.chat.application.dto import ChatRequest, ChatResponse
from app.chat.application.use_cases import AnswerQuestionUseCase

router = APIRouter(prefix="/chat", tags=["chat"])


def _get_use_case(request: Request) -> AnswerQuestionUseCase:
    return request.app.state.answer_question_use_case


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    use_case: AnswerQuestionUseCase = Depends(_get_use_case),
) -> ChatResponse:
    return await use_case.execute(request.messages)
