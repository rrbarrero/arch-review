# Arch Review

Arch Review is a local, reproducible portfolio project for exploring how to build, deploy, and observe a cloud-native LLM application in a controlled Kubernetes environment.

The goal is to implement a FastAPI backend orchestrated with LangGraph that can answer questions over technical documentation using Retrieval-Augmented Generation. The system is intended to combine vector search, a small knowledge graph, source citations, and operational observability.

The project is designed to run on Kubernetes, with infrastructure managed through Pulumi and observability through tools such as LangSmith, Prometheus, and Grafana. The emphasis is architectural clarity: a small, explainable RAG platform that demonstrates deployment, infrastructure as code, tracing, metrics, and documented trade-offs.

## Progress Log

This section tracks the main implementation milestones and architectural decisions as the project evolves.

### 2026-04-26

- Defined the project direction as a Kubernetes-based RAG platform for technical documentation, focused on reproducible infrastructure, observability, and clear architectural trade-offs.
- Added a FastAPI backend skeleton under `app/` and configured Docker Compose to build and run the backend image with `uv`.
- Centralized environment configuration in `.env`, with `env.example` documenting the expected variables for Kind, the backend image, Pulumi, RustFS/S3, and AWS-compatible credentials.
- Added idempotent provisioning scripts for the Kind cluster, the S3-compatible Pulumi state bucket, and the Pulumi `dev` stack under `infra/`.
- Updated the Makefile to orchestrate provisioning steps through scripts instead of embedding operational logic directly in make targets.
