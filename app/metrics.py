from prometheus_client import Counter, Histogram

documents_ingested_total = Counter(
    "documents_ingested_total",
    "Total documents ingested",
    ["content_type", "status"],
)

documents_ingest_errors_total = Counter(
    "documents_ingest_errors_total",
    "Total document ingest errors",
    ["reason"],
)

questions_answered_total = Counter(
    "questions_answered_total",
    "Total questions answered",
)

context_chunks_retrieved = Histogram(
    "context_chunks_retrieved",
    "Number of chunks retrieved per question",
    buckets=(1, 2, 4, 6, 8, 10, 15, 20),
)

chunks_embedded_total = Counter(
    "chunks_embedded_total",
    "Total chunks embedded",
)

chunks_created_total = Counter(
    "chunks_created_total",
    "Total chunks created",
    ["content_type"],
)

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "status"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
