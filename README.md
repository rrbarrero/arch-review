# Arch Review

Arch Review is a reproducible project for building, deploying, and observing a cloud-native LLM application on Kubernetes.

The goal is to implement a FastAPI backend that can ingest technical documentation and source files, enrich them with embeddings and graph context, and answer questions over that knowledge using Retrieval-Augmented Generation. The system is intended to combine vector search, a small knowledge graph, source citations, and operational observability. LangGraph remains part of the intended orchestration direction as the assistant workflow becomes more sophisticated.

![alt text](image.png)

The project is designed to run on Kubernetes, with infrastructure managed through Pulumi and observability through tools such as LangSmith, Prometheus, and Grafana. The emphasis is architectural clarity: a small, explainable RAG platform that demonstrates ingestion, retrieval, deployment, infrastructure as code, tracing, metrics, and documented trade-offs.

## Current Product Surface

The application currently exposes two primary workflows:

- **Document intake**: upload Markdown and Python files from the browser, validate them, split them into retrieval-friendly chunks, generate embeddings, persist them in PostgreSQL with pgvector, and mirror chunk nodes into Neo4j.
- **Architecture review chat**: ask questions over the ingested knowledge through a Next.js chat interface built with `assistant-ui`. The frontend uses a local assistant runtime connected to the FastAPI `/chat` endpoint, which performs vector retrieval over embedded chunks and returns an LLM answer with source citations.

The local development UI is available at `http://localhost:3000` and the backend API at `http://localhost:8000`.

## Quick Start

```bash
make install
```

This command prepares the environment file, starts the supporting services, provisions the Kubernetes and Pulumi resources, builds the backend image, loads it into the cluster, and deploys the application. It is idempotent, so running it multiple times should converge the environment without breaking an existing setup.

For the local Docker Compose development loop:

```bash
make dev
```

The frontend service runs Next.js in development mode so UI changes are reflected without rebuilding the production image. The frontend installs dependencies inside the container using the lockfile before starting.

Useful validation commands:

```bash
make test
make lint
```

![alt text](image-1.png)

## Progress Log

This section tracks the main implementation milestones and architectural decisions as the project evolves.

### 2026-04-27

- Added the first architecture review chat iteration, closing the initial RAG loop from ingestion to question answering.
- Introduced a new `chat` bounded context in the backend with DTOs, retrieval service, answer service, use case, factory, and FastAPI router.
- Added `POST /chat`, accepting chat messages and returning generated answer text plus structured citations.
- Implemented vector retrieval over stored chunk embeddings using pgvector distance search in PostgreSQL.
- Extended the chunk repository contract with semantic search and provided both PostgreSQL and in-memory implementations for runtime and tests.
- Added query embedding support to the embedding service so user questions can be compared against ingested chunks.
- Integrated `assistant-ui` in the Next.js frontend using `LocalRuntime` and a custom `ChatModelAdapter` connected to the FastAPI backend.
- Reworked the main UI into a two-panel workspace: technical sources and intake on the left, review chat on the right.
- Standardized the new chat-facing UI and assistant prompts in English.
- Fixed API response mapping in the frontend so backend `snake_case` responses are converted into frontend `camelCase` models.
- Updated Docker Compose frontend behavior for local development so it runs `next dev` instead of serving a stale production build.
- Added integration tests for the chat use case and HTTP contract, and verified the backend with `make test` and `make lint`.

### 2026-04-26

- Built the first runnable version of the platform, including a FastAPI backend, a Next.js frontend, persistent data services, and automation to recreate the full local environment from a fresh checkout.
- Set up a reproducible cloud-native delivery workflow: container builds, local Kubernetes deployment, infrastructure as code, environment-specific configuration, and database migrations.
- Established a clean backend architecture around domain-driven design principles, separating domain models, application use cases, persistence, external services, and HTTP routing.
- Added the core data layer for a RAG system, combining relational document storage, vector-ready chunks, and a graph representation of documents and relationships.
- Implemented the first end-to-end ingestion flow: uploading Markdown and Python files, validating size and type constraints, splitting content into retrieval-friendly chunks, persisting the results, and returning structured feedback.
- Improved the chunking pipeline with language-aware splitting strategies and hierarchical document processing, preparing the system to support summaries, parent-child context, and more traceable retrieval.
- Integrated local LLM and embedding capabilities so ingested content can be enriched during processing and prepared for semantic search.
- Created an initial browser-based upload experience with client-side validation and real API integration, giving the project a usable product surface rather than only backend endpoints.
- Integrated the Next.js frontend into the infrastructure-as-code deployment, so both frontend and backend are managed as part of the same Kubernetes application.
- Added integration tests across persistence and ingestion behavior, plus automated linting, type checking, database migration management, and CI validation for pull requests.
- Verified the full application running correctly on Kubernetes with the first use case in place: the initial ingestion iteration, embedding generation, and graph enrichment.
