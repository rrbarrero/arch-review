import logging
import time
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.metrics import http_request_duration_seconds, http_requests_total
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.chat.infrastructure.factory import create_answer_question_use_case
from app.chat.infrastructure.routers.chat import router as chat_router
from app.intake.infrastructure.factory import create_ingest_use_case
from app.intake.infrastructure.persistence.postgres import create_pool, ensure_schema
from app.intake.infrastructure.routers.ingest import router as intake_router
from app.settings import Settings

settings = Settings()


def setup_telemetry(otel_settings: Settings) -> None:
    resource = Resource.create({"service.name": otel_settings.otel_service_name})
    provider = TracerProvider(resource=resource)
    span_processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=otel_settings.otel_exporter_otlp_endpoint)
    )
    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)

    LoggingInstrumentor().instrument()
    logging.getLogger().setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    setup_telemetry(settings)

    FastAPIInstrumentor.instrument_app(_app)
    HTTPXClientInstrumentor().instrument()
    PsycopgInstrumentor().instrument()

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


@app.middleware("http")
async def metrics_middleware(request, call_next):
    method = request.method
    path = request.url.path
    start = time.monotonic()
    response = await call_next(request)
    duration = time.monotonic() - start
    status = response.status_code
    http_requests_total.labels(method=method, path=path, status=status).inc()
    http_request_duration_seconds.labels(method=method, path=path, status=status).observe(duration)
    return response


metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    return {"message": "Hello World"}
