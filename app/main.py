from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.chat.infrastructure.factory import create_answer_question_use_case
from app.chat.infrastructure.routers.chat import router as chat_router
from app.intake.infrastructure.factory import create_ingest_use_case
from app.intake.infrastructure.persistence.postgres import create_pool, ensure_schema
from app.intake.infrastructure.routers.ingest import router as intake_router
from app.settings import Settings

settings = Settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    pool = create_pool(settings)
    await pool.open()
    await ensure_schema(pool)
    _app.state.ingest_use_case = create_ingest_use_case(pool)
    _app.state.answer_question_use_case = create_answer_question_use_case(pool)
    yield
    await pool.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(intake_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
