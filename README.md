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

- Built the first runnable version of the platform, including a FastAPI backend, a Next.js frontend, persistent data services, and automation to recreate the full local environment from a fresh checkout.
- Set up a reproducible cloud-native delivery workflow: container build, local Kubernetes deployment, infrastructure as code, environment-specific configuration, and database migrations.
- Established a clean backend architecture around domain-driven design principles, separating domain models, application use cases, persistence, external services, and HTTP routing.
- Added the core data layer for a RAG system, combining relational document storage, vector-ready chunks, and a graph representation of documents and relationships.
- Implemented the first end-to-end ingestion flow: uploading Markdown and Python files, validating size and type constraints, splitting content into retrieval-friendly chunks, persisting the results, and returning structured feedback.
- Improved the chunking pipeline with language-aware splitting strategies and hierarchical document processing, preparing the system to support summaries, parent-child context, and more traceable retrieval.
- Integrated local LLM and embedding capabilities so ingested content can be enriched during processing and prepared for semantic search.
- Created an initial browser-based upload experience with client-side validation and real API integration, giving the project a usable product surface rather than only backend endpoints.
- Added integration tests across persistence and ingestion behavior, plus automated linting, type checking, database migration management, and CI validation for pull requests.
- Verified the full loop from local bootstrap to deployed application response, leaving a stable foundation for the next milestones: retrieval, cited answers, graph-assisted context, and observability.
