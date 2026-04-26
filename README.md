# Arch Review

Arch Review is a reproducible project for building, deploying, and observing a cloud-native LLM application on Kubernetes.

The goal is to implement a FastAPI backend orchestrated with LangGraph that can answer questions over technical documentation using Retrieval-Augmented Generation. The system is intended to combine vector search, a small knowledge graph, source citations, and operational observability.

![alt text](image.png)

The project is designed to run on Kubernetes, with infrastructure managed through Pulumi and observability through tools such as LangSmith, Prometheus, and Grafana. The emphasis is architectural clarity: a small, explainable RAG platform that demonstrates deployment, infrastructure as code, tracing, metrics, and documented trade-offs.

## Quick Start

```bash
make install
```

This command prepares the environment file, starts the supporting services, provisions the Kubernetes and Pulumi resources, builds the backend image, loads it into the cluster, and deploys the application. It is idempotent, so running it multiple times should converge the environment without breaking an existing setup.

![alt text](image-1.png)

## Progress Log

This section tracks the main implementation milestones and architectural decisions as the project evolves.

### 2026-04-26

- Added a FastAPI backend skeleton under `app/` and configured Docker Compose to build and run the backend image with `uv`.
- Centralized environment configuration in `.env`, with `env.example` documenting the expected variables for Kubernetes, the backend image, Pulumi, state management, and cloud-compatible credentials.
- Added idempotent provisioning scripts for Kubernetes infrastructure, Pulumi state management, and the Pulumi `dev` stack under `infra/`.
- Updated the Makefile to orchestrate provisioning steps through scripts instead of embedding operational logic directly in make targets.
- Added Pulumi resources to deploy the FastAPI backend on Kubernetes, including namespace, deployment, service, ingress, and Traefik-based routing.
- Added Makefile targets to build the backend image, load it into the Kubernetes cluster, and deploy the application through Pulumi.
- Verified that the backend is reachable at `http://arch-review.local:8000`.
- Established a stable delivery loop that supports small, incremental changes with fast feedback through image build, cluster load, and Pulumi deployment.
- Added pgvector and Neo4j as RAG data services, available both in Docker Compose for development and in Kubernetes through Pulumi-managed resources.
- Refactored infrastructure configuration so stack-specific values such as service names, ports, storage sizes, images, and Traefik settings are defined in `Pulumi.<stack>.yaml`.
- Added a non-interactive `make install` bootstrap path for quickly reproducing the full environment from a fresh checkout.
- Designed domain models for the intake bounded context following DDD, using Python dataclasses. Value objects: `Source`, `ProcessingStatus`, `ChunkStatus`, `Metadata`. Entities: `Document`, `DocumentChunk`. Repository protocols: `DocumentRepository`, `ChunkRepository`.
- Added `pydantic-settings` for database configuration (`app/settings.py`), loading `PGVECTOR` and `NEO4J` connection parameters from `.env`.
- Installed `psycopg[binary,pool]` for async PostgreSQL access.
- Implemented in-memory (`InMemoryDocumentRepository`, `InMemoryChunkRepository`) and PostgreSQL (`PostgresDocumentRepository`, `PostgresChunkRepository`) repository variants under `app/intake/infrastructure/persistence/`.
- Added 12 integration tests in `tests/integration/test_repositories.py` that run the same scenarios against both implementations, verifying save, find, upsert, delete, batch save, status filtering, and cascade delete. Postgres tables are cleaned up after the test session.
- Added `make test` to run tests inside Docker.
- Added `ruff` and `ty` (Astral's Rust-based Python type checker) as dev dependencies, with `make ruff`, `make ty`, and `make lint` targets. The `ty` target runs in strict mode and excludes `infra/`.
- Added `dbmate` service in Docker Compose for database migration management. Initial migration creates `documents` and `chunks` tables with vector extension, foreign keys, and indexes. Use `make dbmate` to apply pending migrations.
- Added `.github/workflows/ci.yml` with lint (`make ruff`), type checking (`make ty`), and test (`make test`) steps running on push/PR to `main`.
- Implemented use case #1: file ingestion (`IngestDocumentsUseCase`). `POST /intake/ingest` accepts `.md` and `.py` files (max 500 KB each, batch upload), chunks them by paragraphs, and persists documents + chunks via the repository layer.
- Added `ChunkingService` (domain service) for text splitting, and `FileInput`/`IngestDocumentsOutput` DTOs.
- Added 8 integration tests for the ingestion use case using in-memory repositories, covering single/multiple files, extension validation, size limits, partial failures, and empty inputs.
- Replaced the manual paragraph chunker with `langchain-text-splitters` using `RecursiveCharacterTextSplitter` with per-language separators for Markdown and Python. The chunking strategies follow a Strategy pattern: `MarkdownChunkingStrategy` and `PythonChunkingStrategy` implement the `ChunkingStrategy` protocol, selected by `ChunkingService` based on content type.
- Added the RAPTOR (Recursive Abstractive Processing for Tree-Organized Retrieval) pattern via `RaptorService`. After initial chunking, the service clusters consecutive chunks, summarizes each cluster (placeholder concatenation), and recurses until a single root summary remains. The resulting hierarchy is stored on `DocumentChunk` via `level` and `parent_ids` fields. 5 integration tests cover multi-level tree building, leaf preservation, and single-chunk edge cases.
- Added `langchain-ollama` with an LLM factory in `app/llm.py` (`get_llm`, `get_embeddings` with `@lru_cache`), configured via `OLLAMA_BASE_URL`, `LLM_MODEL`, `LLM_TEMPERATURE`, and `EMBEDDING_MODEL` in `.env`.
- Added `app/__init__.py` and configured CORS via `CORSMiddleware` with origins from `Settings.cors_origins` (parsed from `CORS_ORIGINS_RAW` env var).
- Created a Next.js frontend under `frontend/` with TypeScript, Tailwind CSS 4, shadcn, Zod, Vitest, ESLint, and Prettier. The DDD structure mirrors the backend (`domain/`, `infrastructure/api/`, `hooks/`). The upload form (`IngestForm`) validates files client-side and sends them to `POST /intake/ingest`.
- Added `make dev` to start the full stack: databases, migrations, backend (`localhost:8000`), and frontend (`localhost:3000`).
- Added `EmbeddingService` that generates embeddings via `OllamaEmbeddings.aembed_documents()` during ingestion, storing them in `chunks.embedding` and setting status to `EMBEDDED`.
- Added `Neo4jGraphService` that creates `:Document` and `:Chunk` nodes with `PART_OF` and `NEXT` relationships during ingestion, storing the Neo4j node ID in `chunks.graph_node_id` and setting status to `GRAPH_PROCESSED`.
- Wired both services into the ingestion pipeline via `app/intake/infrastructure/factory.py`. The use case is injected into the endpoint via FastAPI `Depends`, allowing easy override in tests with `app.dependency_overrides`.
